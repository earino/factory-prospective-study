"""Self-contained XGBoost solution: one XGBClassifier on numeric features, native low-cardinality
categoricals, and smoothed out-of-fold target encodings of state/agency-style interactions.

Availability notes: only the release's 18 declared predictors are used (no date, no ID, no target).
Target encodings are learned from the fitting partition labels only; training rows receive
out-of-fold values computed on contiguous row blocks (training rows arrive in chronological order),
so a row's own label never enters its own encoding, prior or smoothing. Scoring rows use the
full-fitting-partition tables stored in the returned state. prepare() is strictly row-wise.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = dict(
    params=dict(n_estimators=100, max_depth=8, learning_rate=0.02, subsample=0.8,
                colsample_bytree=0.5, min_child_weight=5),
    native=['facility_type_code', 'air_pollutant_class_code', 'comp_monitor_type_code', 'state_epa_flag'],
    te=[['state'], ['state', 'state_epa_flag'], ['state', 'air_pollutant_class_code'],
        ['epa_region', 'air_pollutant_class_code'], ['naics_2digit', 'air_pollutant_class_code'],
        ['state', 'comp_monitor_type_code']],
    te_m=50.0, te_folds=5, extra=[],
    # label-free group aggregates of history indicators: (group keys, indicator name)
    xagg=[(['state'], 'rec5y'), (['state'], 'st')], xagg_m=20.0, drop=('prior_evaluations_3y',))
COLS = ['state', 'epa_region', 'sic_2digit', 'naics_2digit', 'facility_type_code', 'air_pollutant_class_code',
        'program_count', 'pollutant_count', 'comp_monitor_type_code', 'state_epa_flag', 'prior_evaluations_3y',
        'days_since_last_evaluation', 'prior_stack_test_failures_3y', 'prior_hpv_count',
        'days_since_hpv_resolution', 'prior_formal_actions_3y', 'prior_penalties_3y', 'prior_tv_deviations_3y']
STR = ['state', 'facility_type_code', 'air_pollutant_class_code', 'comp_monitor_type_code', 'state_epa_flag']


def _key(v):
    return 'NA' if v is None or v != v else (v if isinstance(v, str) else float(v))


def _num(v):
    return float('nan') if v is None else float(v)


def _te_tables(rows, y, keys):
    t = {}
    for r, yy in zip(rows, y):
        k = tuple(_key(r[c]) for c in keys)
        a = t.get(k)
        if a is None:
            t[k] = [int(yy), 1]
        else:
            a[0] += int(yy); a[1] += 1
    return t


def _te_val(t, k, prior, m):
    a = t.get(k)
    return prior if a is None else (a[0] + m * prior) / (a[1] + m)


def fit(X_train, y_train, *, seed, threads):
    cfg = CFG
    X = X_train[COLS]
    rows = [dict(zip(COLS, r)) for r in X.to_numpy(dtype=object)]
    y = np.asarray(y_train).astype(int); n = len(y)
    state = {"cfg": cfg}
    state['levels'] = {c: {v: i for i, v in enumerate(sorted({_key(r[c]) for r in rows} - {'NA'}, key=str))}
                       for c in cfg['native']}
    state['prior'] = float(y.mean())
    state['te'] = {tuple(keys): {k: (v[0], v[1]) for k, v in _te_tables(rows, y, keys).items()} for keys in cfg['te']}
    # Label-free aggregates: smoothed group means of history indicators over the fitting rows (no labels used).
    state['xagg'] = []
    for keys, nm in cfg.get('xagg', []):
        t = {}; tot = 0.0
        for r in rows:
            v = _stat(r, nm); tot += v
            k = tuple(_key(r[c]) for c in keys)
            a = t.get(k)
            if a is None:
                t[k] = [v, 1]
            else:
                a[0] += v; a[1] += 1
        state['xagg'].append((tuple(keys), nm, {k: (a[0], a[1]) for k, a in t.items()}, tot / n))
    F = prepare(state, X)
    names = _names(cfg)
    state['names'] = names
    # Out-of-fold target encodings for the training rows (contiguous blocks of the supplied row order).
    K = cfg['te_folds']
    fold = np.arange(n) * K // n
    for keys in cfg['te']:
        j = names.index('te_' + '_'.join(keys))
        for f in range(K):
            inn = np.where(fold != f)[0]; out = np.where(fold == f)[0]
            yi = y[inn]; pr = float(yi.mean())
            t = _te_tables([rows[i] for i in inn], yi, keys)
            for i in out:
                F[i, j] = _te_val(t, tuple(_key(rows[i][c]) for c in keys), pr, cfg['te_m'])
    ft = ['c' if nm in cfg['native'] else 'q' for nm in names]
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, feature_types=ft,
                          random_state=seed, n_jobs=threads, **cfg['params'])
    m.fit(F, y)
    state["model"] = m
    return state


def _names(cfg):
    names = [c for c in COLS if (c in cfg['native'] or c not in STR) and c not in cfg.get('drop', ())]
    names += ['te_' + '_'.join(keys) for keys in cfg['te']]
    names += list(cfg['extra'])
    names += ['xa_' + '_'.join(keys) + '_' + nm for keys, nm in cfg.get('xagg', [])]
    return names


def _stat(r, nm):
    if nm == 'rec5y':
        d = _num(r['days_since_hpv_resolution']); return 1.0 if d < 1825 else 0.0
    if nm == 'st':
        return 1.0 if _num(r['prior_stack_test_failures_3y']) > 0 else 0.0
    if nm == 'anyhpv':
        return 1.0 if _num(r['prior_hpv_count']) > 0 else 0.0
    if nm == 'fa':
        return 1.0 if _num(r['prior_formal_actions_3y']) > 0 else 0.0
    raise KeyError(nm)


def prepare(state, X):
    cfg = state['cfg']; nan = float('nan'); drop = cfg.get('drop', ())
    cols = list(X.columns); A = X.to_numpy(dtype=object)
    out = []
    for ri in range(A.shape[0]):
        r = dict(zip(cols, A[ri])); f = []
        for c in COLS:
            if c in drop:
                continue
            if c in cfg['native']:
                f.append(state['levels'][c].get(_key(r[c]), nan))
            elif c not in STR:
                f.append(_num(r[c]))
        for keys, t in state['te'].items():
            f.append(_te_val(t, tuple(_key(r[c]) for c in keys), state['prior'], cfg['te_m']))
        if cfg['extra']:
            E = _extra(r)
            for nm in cfg['extra']:
                f.append(E[nm])
        for keys, nm, t, pr in state.get('xagg', []):
            f.append(_te_val(t, tuple(_key(r[c]) for c in keys), pr, cfg['xagg_m']))
        out.append(f)
    return np.asarray(out, dtype=np.float32)


def _extra(r):
    hp = _num(r['prior_hpv_count']); d = _num(r['days_since_hpv_resolution'])
    fa = _num(r['prior_formal_actions_3y']); st = _num(r['prior_stack_test_failures_3y'])
    tv = _num(r['prior_tv_deviations_3y']); pe = _num(r['prior_evaluations_3y'])
    dl = _num(r['days_since_last_evaluation']); pc = _num(r['program_count'])
    po = _num(r['pollutant_count']); pen = _num(r['prior_penalties_3y'])
    return {'hpv_rate': hp / (d + 365.0), 'enf_sum': fa + st + tv,
            'enf_any': float((fa > 0) + (st > 0) + (tv > 0) + (hp > 0)),
            'pen_per_action': pen / (fa + 1.0), 'ev_x_gap': dl * (pe + 1.0),
            'poll_per_prog': po / pc if pc else float('nan'), 'hp_per_eval': hp / (pe + 1.0)}
