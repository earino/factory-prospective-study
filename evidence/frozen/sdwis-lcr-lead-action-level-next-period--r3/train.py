"""Self-contained XGBoost solution (frozen from diag/cand.py by diag/make_train.py)."""
import numpy as np
import pandas as pd
import xgboost as xgb
CFG = {'agency': ['ord', 'oh', 'agstat'],
 'drop': (),
 'feats': 'all',
 'mono': False,
 'params': {'colsample_bytree': 0.8,
            'learning_rate': 0.03,
            'max_depth': 4,
            'min_child_weight': 5,
            'n_estimators': 400,
            'reg_lambda': 5.0,
            'subsample': 0.8},
 'te_folds': 5,
 'te_smooth': 50.0}
NUM = ['prior_pb90_mg_l','prior_cu90_mg_l','pb90_change_from_previous','n_prior_periods_observed','ever_exceeded_before','gap_days_between_periods','prior_period_length_days','population_served_count','prior_lcr_violations_count','prior_lslr_milestone']
CATS = ['primary_source_code','owner_type_code','primacy_agency_code']

def _base(X):
    g = lambda c: X[c].to_numpy(dtype=float)
    pb = g('prior_pb90_mg_l'); ch = g('pb90_change_from_previous'); cu = g('prior_cu90_mg_l')
    n = g('n_prior_periods_observed'); gap = g('gap_days_between_periods'); pl = g('prior_period_length_days')
    viol = g('prior_lcr_violations_count'); pop = g('population_served_count')
    pp = pb - ch
    fix = lambda v: np.where(v >= 0.75, v / 1000.0, v)
    pbf = fix(pb); ppf = fix(pp)
    cuf = np.where(cu >= 20, cu / 1000.0, cu)
    d = {
        'pb': pb, 'cu': cu, 'ch': ch, 'n': n, 'ever': g('ever_exceeded_before'), 'gap': gap, 'pl': pl, 'pop': pop,
        'viol': viol, 'lslr': g('prior_lslr_milestone'),
        'pbf': pbf, 'ppf': ppf, 'unit': (pb >= 0.75).astype(float),
        'mx': np.fmax(pbf, ppf), 'mn2': np.where(np.isnan(ppf), pbf, (pbf + ppf) / 2), 'chf': pbf - ppf,
        'cuf': cuf, 'viol_rate': viol / n, 'span': gap + pl,
        'nexc2': (pbf > 0.015).astype(float) + np.where(np.isnan(ppf), 0, ppf > 0.015),
        'pb_ug_frac': np.abs(pb * 1000 - np.round(pb * 1000)),
        'ever_not_recent': g('ever_exceeded_before') - (np.fmax(pbf, ppf) > 0.015),
        'lr': np.log((pbf + 1e-4) / (ppf + 1e-4)), 'gm': np.sqrt((pbf + 1e-4) * (np.where(np.isnan(ppf), pbf, ppf) + 1e-4)),
        'pl_mod': np.where(pl < 250, pl - 182.5, np.where(pl < 500, pl - 365, np.where(pl < 1500, pl - 1095, np.nan))),
        'sched': np.where(pl < 150, 0, np.where(pl < 250, 1, np.where(pl < 340, 2, np.where(pl < 500, 3, np.where(pl < 1090, 4, np.where(pl < 1100, 5, 6)))))).astype(float),
        'lpop': np.log1p(pop), 'zero2': (pb == 0).astype(float) + np.where(np.isnan(pp), 0, pp == 0),
    }
    return d

def _cat_codes(state, X):
    out = {}
    for c in CATS:
        v = X[c].to_numpy()
        m = state['maps'][c]
        out[c] = np.array([m.get(x, np.nan) for x in v], dtype=float)
    return out

def _te_fit(key, y, folds, smooth, seed):
    prior = y.mean()
    rng = np.random.RandomState(seed)
    f = rng.randint(0, folds, len(y))
    oof = np.full(len(y), np.nan)
    df = pd.DataFrame({'k': key, 'y': y, 'f': f})
    tot = df.groupby('k')['y'].agg(['sum', 'count'])
    pf = df.groupby(['k', 'f'])['y'].agg(['sum', 'count'])
    for i in range(folds):
        mask = f == i
        ytr = y[~mask]; pr = ytr.mean()
        k = df.loc[mask, 'k']
        s = tot['sum'].reindex(k).to_numpy(); c = tot['count'].reindex(k).to_numpy()
        idx = pd.MultiIndex.from_arrays([k, np.full(mask.sum(), i)])
        s2 = pf['sum'].reindex(idx).fillna(0).to_numpy(); c2 = pf['count'].reindex(idx).fillna(0).to_numpy()
        oof[mask] = (s - s2 + smooth * pr) / (c - c2 + smooth)
    full = ((tot['sum'] + smooth * prior) / (tot['count'] + smooth)).to_dict()
    return oof, full, prior

def _matrix(state, X, te=None):
    d = _base(X)
    cc = _cat_codes(state, X)
    cols = []
    for name in state['names']:
        if name in d: cols.append(d[name])
        elif name in cc: cols.append(cc[name])
        elif name.startswith('oh_'):
            cols.append((X['primacy_agency_code'].to_numpy() == name[3:]).astype(float))
        elif name.startswith('as_'):
            m = state['agstat'][name]
            cols.append(np.array([m.get(x, np.nan) for x in X['primacy_agency_code'].to_numpy()], dtype=float))
        elif name.startswith('rel_'):
            m = state['agstat'][name]
            cols.append(d['pbf'] - np.array([m.get(x, np.nan) for x in X['primacy_agency_code'].to_numpy()], dtype=float))
        elif name.startswith('te_'):
            if te is not None: cols.append(te[name])
            else:
                k = _key(name, X, d)
                m, prior = state['te'][name]
                cols.append(np.array([m.get(x, prior) for x in k], dtype=float))
        else: raise KeyError(name)
    return np.column_stack(cols).astype(np.float32)

def _key(name, X, d):
    ag = X['primacy_agency_code'].astype(str).to_numpy().astype('U')
    if name == 'te_ag': return ag
    if name == 'te_ag_exc': return np.char.add(ag, np.where(d['pbf'] > 0.015, '_1', '_0'))
    if name == 'te_ag_pl':
        pl = d['pl']; b = np.where(pl < 250, 'h', np.where(pl < 500, 'a', 't'))
        return np.char.add(np.char.add(ag, '_'), b)
    if name == 'te_ag_own': return np.char.add(np.char.add(ag, '_'), X['owner_type_code'].astype(str).to_numpy().astype('U'))
    if name == 'te_ag_src': return np.char.add(np.char.add(ag, '_'), X['primary_source_code'].astype(str).to_numpy().astype('U'))
    if name == 'te_ag_zero': return np.char.add(ag, np.where(d['pb'] == 0, '_z', '_n'))
    raise KeyError(name)

FEATSETS = {
    'raw': ['pb','cu','ch','n','ever','gap','pl','pop','viol','lslr'],
    'all': ['pb','cu','ch','n','ever','gap','pl','pop','viol','lslr','pbf','ppf','unit','mx','mn2','chf','cuf','viol_rate','span','nexc2','pb_ug_frac','ever_not_recent'],
}

def fit(X_train, y_train, *, seed, threads):
    cfg = CFG
    y = np.asarray(y_train).astype(int)
    state = {'maps': {c: {v: i for i, v in enumerate(sorted(X_train[c].dropna().unique()))} for c in CATS}}
    names = list(FEATSETS[cfg['feats']]) if isinstance(cfg['feats'], str) else list(cfg['feats'])
    names += list(cfg.get('extra', ())) + ['primary_source_code', 'owner_type_code']
    tenames = []
    if cfg['agency'] == 'ord': names.append('primacy_agency_code')
    elif cfg['agency'] == 'none': pass
    else:
        if 'ord' in cfg['agency']: names.append('primacy_agency_code')
        tenames = [t for t in cfg['agency'] if t.startswith('te_')]
        names += tenames
    if 'oh' in cfg['agency']: names += ['oh_' + a for a in sorted(X_train['primacy_agency_code'].dropna().unique())]
    if 'agstat' in cfg['agency']:
        d0 = _base(X_train); ag0 = X_train['primacy_agency_code']
        st = {'as_lpb': np.log1p(d0['pbf'] * 1000), 'as_zero': (d0['pb'] == 0).astype(float), 'as_exc': (d0['pbf'] > 0.015).astype(float),
              'as_pl': d0['pl'], 'as_gap1': (d0['gap'] == 1).astype(float), 'as_cu': (~np.isnan(d0['cu'])).astype(float), 'as_viol': d0['viol_rate']}
        state['agstat'] = {k: pd.Series(v).groupby(ag0.to_numpy()).mean().to_dict() for k, v in st.items()}
        names += list(st)
    if 'agrel' in cfg['agency']:
        d0 = _base(X_train); ag0 = X_train['primacy_agency_code'].to_numpy()
        state.setdefault('agstat', {})
        state['agstat']['rel_med'] = pd.Series(d0['pbf']).groupby(ag0).median().to_dict()
        state['agstat']['rel_q90'] = pd.Series(d0['pbf']).groupby(ag0).quantile(0.9).to_dict()
        names += ['rel_med', 'rel_q90']
    names = [n for n in names if n not in cfg['drop']]
    tenames = [n for n in tenames if n in names]
    state['names'] = names
    d = _base(X_train)
    te_oof = {}; state['te'] = {}
    for t in tenames:
        oof, full, prior = _te_fit(_key(t, X_train, d), y, cfg['te_folds'], cfg['te_smooth'], seed)
        te_oof[t] = oof; state['te'][t] = (full, prior)
    Z = _matrix(state, X_train, te=te_oof)
    p = dict(cfg['params'])
    if cfg['mono']:
        mc = {'pbf': 0, 'mx': 1, 'mn2': 0, 'ever': 1, 'nexc2': 1}
        p['monotone_constraints'] = '(' + ','.join(str(mc.get(n, 0)) for n in names) + ')'
    w = None
    if cfg.get('recency'):
        w = np.exp(-(len(y) - 1 - np.arange(len(y))) / (cfg['recency'] * len(y)))
    m = xgb.XGBClassifier(tree_method='hist', random_state=seed, n_jobs=threads, **p)
    m.fit(Z, y, sample_weight=w)
    state['model'] = m
    return state

def prepare(state, X):
    return _matrix(state, X)
