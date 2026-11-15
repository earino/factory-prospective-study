"""Self-contained XGBoost solution (CFG selects the tested variant)."""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {'params': {'n_estimators': 400,
            'max_depth': 4,
            'learning_rate': 0.03,
            'subsample': 0.8,
            'colsample_bytree': 0.7,
            'min_child_weight': 10,
            'reg_lambda': 5,
            'max_cat_threshold': 8},
 'derived': True,
 'cat_mode': 'native',
 'te_smooth': 50.0,
 'te_folds': 5,
 'drop': ('population_served_count', 'log_pop'),
 'mono': {'ever_exceeded_before': 1,
          'max2_fix': 1,
          'pb_fix': 1,
          'mean2_fix': 1,
          'prior_lcr_violations_count': 1,
          'viol_per_period': 1,
          'cu_flag': 1},
 'recency': 1,
 'pop_cls': True}
NUM = ["prior_pb90_mg_l", "prior_cu90_mg_l", "pb90_change_from_previous", "n_prior_periods_observed",
       "ever_exceeded_before", "gap_days_between_periods", "prior_period_length_days",
       "population_served_count", "prior_lcr_violations_count", "prior_lslr_milestone"]
CATS = ["primary_source_code", "owner_type_code", "primacy_agency_code"]


def _key(v):
    return "nan" if (v is None or v != v) else str(v)


def _raw(X):
    num = {c: pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float) for c in NUM}
    cat = {c: [_key(v) for v in X[c].tolist()] for c in CATS}
    aux = {"pb_bin": np.digitize(_fix(num["prior_pb90_mg_l"]), [1e-9, .002, .005, .010, .015, .03]),
           "pop_cls": np.digitize(num["population_served_count"], [101, 501, 3301, 10001, 50001, 100001]),
           "plen_cls": np.digitize(num["prior_period_length_days"], [200, 400, 800, 1200])}
    cat.update({k: [str(int(v)) for v in a] for k, a in aux.items()})
    return num, cat


def _fix(v):
    # values >= 1 mg/L behave like ug/L entries (unit slips); rescale
    return np.where(v >= 1.0, v / 1000.0, v)


def _features(state, num, cat):
    cfg = state["cfg"]
    f = {}
    pb = num["prior_pb90_mg_l"]; ch = num["pb90_change_from_previous"]
    for c in NUM:
        f[c] = num[c]
    if cfg["derived"]:
        prev = pb - ch
        pbf = _fix(pb); prf = _fix(prev)
        f["prev_pb"] = prev
        f["pb_fix"] = pbf
        f["prev_fix"] = prf
        f["max2_fix"] = np.fmax(pbf, prf)
        f["min2_fix"] = np.fmin(pbf, prf)
        f["mean2_fix"] = np.where(np.isnan(prf), pbf, (pbf + prf) / 2)
        f["unit_slip"] = (pb >= 1.0).astype(float)
        npr = num["n_prior_periods_observed"]
        f["viol_per_period"] = num["prior_lcr_violations_count"] / np.maximum(npr, 1)
        f["span"] = num["gap_days_between_periods"] + num["prior_period_length_days"]
        f["cu_flag"] = (~np.isnan(num["prior_cu90_mg_l"])).astype(float)
        f["pb_frac"] = np.round((pb * 1000.0) % 1.0, 4)
        if cfg.get("epp"):
            f["ever_per_period"] = num["ever_exceeded_before"] / np.maximum(npr, 1)
            f["both_low"] = ((np.fmax(pbf, prf) <= 0.005) & (num["ever_exceeded_before"] == 0)).astype(float)
        if cfg.get("proj"):
            lp = np.log(pbf + 0.001); lq = np.log(prf + 0.001)
            f["logmean2"] = np.where(np.isnan(lq), lp, (lp + lq) / 2)
            f["wmean2"] = np.where(np.isnan(prf), pbf, 0.67 * pbf + 0.33 * prf)
            f["logdiff2"] = lp - lq
        f["log_pop"] = np.log1p(np.maximum(num["population_served_count"], 0))
    if cfg.get("agency_stats"):
        ag = cat["primacy_agency_code"]; pbf2 = _fix(pb); A = state["agency"]
        rank = np.full(len(pb), np.nan); same = np.full(len(pb), np.nan)
        desc = {k: np.full(len(pb), np.nan) for k in state["agency_desc_names"]}
        for i, a in enumerate(ag):
            t = A.get(a)
            if t is None:
                continue
            srt = t["sorted"]
            lo = np.searchsorted(srt, pbf2[i], "left"); hi = np.searchsorted(srt, pbf2[i], "right")
            rank[i] = (lo + hi) / (2.0 * len(srt)); same[i] = (hi - lo) / float(len(srt))
            for k in desc:
                desc[k][i] = t[k]
        f["ag_pb_rank"] = rank; f["ag_pb_same"] = same
        if cfg["agency_stats"] == "full":
            for k in desc:
                f["ag_" + k] = desc[k]
    if cfg.get("pop_cls"):
        f["pop_cls"] = np.digitize(num["population_served_count"], [101, 501, 3301, 10001, 50001, 100001]).astype(float)
    if cfg.get("ordte"):
        for h in cfg["ordte"]:
            tab = state["ordte"][h]["final"]; pr = state["ordte"][h]["final_prior"]
            f["ag_recent_%s" % h] = np.array([tab.get(a, pr) for a in cat["primacy_agency_code"]], dtype=float)
    mode = cfg["cat_mode"]
    for c in CATS:
        if mode in ("native", "both", "code"):
            lv = state["levels"][c]
            f[c] = np.array([lv.get(k, np.nan) for k in cat[c]], dtype=float)
    if mode in ("te", "both"):
        for name, keys in state["te_keys"].items():
            tab = state["te"][name]; prior = state["prior"]
            ks = _te_key(name, keys, num, cat)
            f["te_" + name] = np.array([tab.get(k, prior) for k in ks], dtype=float)
    return f


def _te_key(name, keys, num, cat):
    parts = []
    for k in keys:
        if k in cat:
            parts.append(cat[k])
        else:
            parts.append([str(int(v)) if v == v else "nan" for v in num[k]])
    return ["|".join(t) for t in zip(*parts)]


TE_KEYS = {"agency": ["primacy_agency_code"],
           "agency_pb": ["primacy_agency_code", "pb_bin"],
           "agency_pop": ["primacy_agency_code", "pop_cls"],
           "agency_plen": ["primacy_agency_code", "plen_cls"],
           "pop_pb": ["pop_cls", "pb_bin"],
           "agency_ever": ["primacy_agency_code", "ever_exceeded_before"],
           "agency_src": ["primacy_agency_code", "primary_source_code"],
           "owner_src": ["owner_type_code", "primary_source_code"]}


def _te_table(keys, y, prior, m):
    s = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    return dict(zip(s.index, (s["sum"] + prior * m) / (s["count"] + m)))


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    y = np.asarray(y_train).astype(int)
    num, cat = _raw(X_train)
    state = {"cfg": cfg, "levels": {c: {k: i for i, k in enumerate(sorted(set(cat[c]) - {"nan"}))} for c in CATS},
             "te_keys": {k: TE_KEYS[k] for k in cfg.get("te_use", list(TE_KEYS))}, "prior": float(y.mean())}
    state["agency_desc_names"] = ["zero_share", "med_pb", "p90_pb", "tri_share", "semi_share", "mean_nprior", "n"]
    if cfg.get("agency_stats"):
        d = pd.DataFrame({"a": cat["primacy_agency_code"], "pb": _fix(num["prior_pb90_mg_l"]),
                          "pl": num["prior_period_length_days"], "np": num["n_prior_periods_observed"]})
        state["agency"] = {}
        for a, g in d.groupby("a"):
            v = np.sort(g["pb"].to_numpy())
            state["agency"][a] = {"sorted": v, "zero_share": float((v == 0).mean()), "med_pb": float(np.median(v)),
                                  "p90_pb": float(np.quantile(v, .9)), "tri_share": float((g["pl"] > 900).mean()),
                                  "semi_share": float((g["pl"] < 200).mean()), "mean_nprior": float(g["np"].mean()),
                                  "n": float(len(g))}
    oof = {}
    if cfg.get("ordte"):
        # ordered (past-only) agency rate: training rows arrive in chronological order; a row in block b
        # is encoded from blocks < b only, exponentially decayed; prediction uses all blocks.
        nb = cfg.get("ordte_blocks", 20); msm = cfg.get("ordte_smooth", 30.0)
        blk = np.minimum((np.arange(len(y)) * nb) // max(len(y), 1), nb - 1)
        ag = np.array(cat["primacy_agency_code"], dtype=object)
        cnt = pd.crosstab(ag, blk).reindex(columns=range(nb), fill_value=0)
        pos = pd.crosstab(ag, blk, values=y, aggfunc="sum").reindex(columns=range(nb), fill_value=0).fillna(0)
        idx = {a: i for i, a in enumerate(cnt.index)}; C = cnt.to_numpy(float); P = pos.to_numpy(float)
        rows = np.array([idx[a] for a in ag])
        state["ordte"] = {}
        for h in cfg["ordte"]:
            enc = np.full(len(y), np.nan)
            for b in range(1, nb + 1):
                wj = 0.5 ** ((b - 1 - np.arange(b)) / float(h))
                c = C[:, :b] @ wj; p = P[:, :b] @ wj; pr = p.sum() / max(c.sum(), 1e-9)
                r = (p + pr * msm) / (c + msm)
                if b < nb:
                    sel = blk == b; enc[sel] = r[rows[sel]]
                else:
                    state["ordte"][h] = {"final": {a: float(r[i]) for a, i in idx.items()}, "final_prior": float(pr)}
            oof["ag_recent_%s" % h] = enc
    if cfg["cat_mode"] in ("te", "both"):
        rng = np.random.RandomState(seed); fold = rng.randint(0, cfg["te_folds"], len(y))
        state["te"] = {}
        for name, keys in state["te_keys"].items():
            ks = np.array(_te_key(name, keys, num, cat), dtype=object)
            state["te"][name] = _te_table(ks, y, state["prior"], cfg["te_smooth"])
            o = np.empty(len(y))
            for k in range(cfg["te_folds"]):
                tr = fold != k; pr = float(y[tr].mean())
                tab = _te_table(ks[tr], y[tr], pr, cfg["te_smooth"])
                o[~tr] = [tab.get(v, pr) for v in ks[~tr]]
            oof["te_" + name] = o
    f = _features(state, num, cat)
    f.update(oof)
    names = [n for n in f if n not in cfg["drop"]]
    state["names"] = names
    ftypes = ["c" if (n in CATS and cfg["cat_mode"] in ("native", "both")) else "q" for n in names]
    M = np.column_stack([f[n] for n in names])
    extra = {}
    if cfg.get("mono"):
        extra["monotone_constraints"] = "(" + ",".join(str(int(cfg["mono"].get(n, 0))) for n in names) + ")"
    if cfg.get("fw"):
        extra["feature_weights"] = np.array([float(cfg["fw"].get(n, 1.0)) for n in names])
    if cfg.get("ic_additive"):
        grp = [i for i, n in enumerate(names) if n in cfg["ic_additive"]]
        rest = [i for i, n in enumerate(names) if n not in cfg["ic_additive"] or n in cfg.get("ic_shared", ())]
        extra["interaction_constraints"] = str([grp, rest])
    w = None
    if cfg.get("skip_first"):
        w = (np.arange(len(y)) >= cfg["skip_first"] * len(y)).astype(float)
    if cfg.get("span_w"):
        sp = np.clip(num["gap_days_between_periods"] + num["prior_period_length_days"], 180, 1100) / 365.0
        w = sp ** cfg["span_w"] if w is None else w * sp ** cfg["span_w"]
    if cfg.get("recency"):
        # training rows arrive in chronological file order; down-weight the oldest rows
        r = np.exp(-cfg["recency"] * (1.0 - np.arange(len(y)) / max(len(y) - 1, 1)))
        w = r if w is None else w * r
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, feature_types=ftypes,
                          random_state=seed, n_jobs=threads, **extra, **cfg["params"])
    m.fit(M, y, sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    num, cat = _raw(X)
    f = _features(state, num, cat)
    return np.column_stack([f[n] for n in state["names"]])
