"""Self-contained XGBoost solution. Change this file; use evaluate.py to test.

As left: the H2 configuration (trial a6f1894a, validation AUC 0.86445). Options that are off by default
(eng, mono, qbins, fixed_edges, agg, te_mode="ordered") were tested and not adopted; see LOG.md.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {"n_estimators": 400, "max_depth": 4, "learning_rate": 0.03, "subsample": 0.7, "colsample_bytree": 0.7,
          "min_child_weight": 5, "reg_lambda": 5, "max_bin": 8}
CATS = ["state", "facility_type_code", "air_pollutant_class_code", "comp_monitor_type_code", "state_epa_flag"]
NUMS = ["epa_region", "sic_2digit", "naics_2digit", "program_count", "pollutant_count", "prior_evaluations_3y",
        "days_since_last_evaluation", "prior_stack_test_failures_3y", "prior_hpv_count", "days_since_hpv_resolution",
        "prior_formal_actions_3y", "prior_penalties_3y", "prior_tv_deviations_3y"]
# Out-of-fold target-encoded keys (tuples of raw columns).
TE_KEYS = [("state",), ("state", "air_pollutant_class_code"), ("state", "state_epa_flag")]
# H3 variant (preferred by training-only folds): add ("air_pollutant_class_code", "naics_2digit") to TE_KEYS,
# set CFG eng=True, te_m=100.0 and PARAMS n_estimators=300.
CFG = {"cat_mode": "native", "te": True, "te_m": 300.0, "te_folds": 5, "eng": False, "drop": [], "mono": False, "qbins": {}}
MONO_UP = ["prior_hpv_count", "prior_formal_actions_3y", "prior_penalties_3y", "prior_tv_deviations_3y",
           "prior_stack_test_failures_3y", "viol_sum"]


# Label-free state-level aggregates of history features (agency enforcement-style descriptors).
AGGS = ["hpv_any", "hpv_recent", "stack_any", "action_any", "tv_any", "maj", "n_eval"]


def _agg_frame(X):
    return pd.DataFrame({
        "state": X["state"].astype(object).where(X["state"].notna(), "NA").to_numpy(),
        "hpv_any": (X["prior_hpv_count"] > 0).to_numpy(dtype=float),
        "hpv_recent": (X["days_since_hpv_resolution"] < 1095).to_numpy(dtype=float),
        "stack_any": (X["prior_stack_test_failures_3y"] > 0).to_numpy(dtype=float),
        "action_any": (X["prior_formal_actions_3y"] > 0).to_numpy(dtype=float),
        "tv_any": (X["prior_tv_deviations_3y"] > 0).to_numpy(dtype=float),
        "maj": (X["air_pollutant_class_code"] == "MAJ").to_numpy(dtype=float),
        "n_eval": np.minimum(X["prior_evaluations_3y"].to_numpy(dtype=float), 20.0),
    })


def _col(X, c):
    # Derived row-wise key parts (history flags) besides raw categorical columns.
    if c == "hpv_any":
        return (X["prior_hpv_count"] > 0).astype(int).astype(str).tolist()
    if c == "hpv_recent":
        return (X["days_since_hpv_resolution"] < 1095).astype(int).astype(str).tolist()
    if c == "stack_any":
        return (X["prior_stack_test_failures_3y"] > 0).astype(int).astype(str).tolist()
    if c == "action_any":
        return (X["prior_formal_actions_3y"] > 0).astype(int).astype(str).tolist()
    return X[c].astype(object).where(X[c].notna(), "NA").astype(str).tolist()


def _keys(X, cols):
    return ["|".join(t) for t in zip(*[_col(X, c) for c in cols])]


def _te_table(keys, y, prior, m):
    s = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    return ((s["sum"] + prior * m) / (s["count"] + m)).to_dict()


def _names(cfg):
    names = list(CATS) + list(NUMS)
    if cfg["eng"]:
        names += ["viol_sum", "pen_per_action", "poll_per_prog", "hpv_recency", "eval_recency"]
    if cfg["te"]:
        names += ["te_" + "_".join(k) for k in TE_KEYS]
    if cfg.get("agg"):
        names += ["sa_" + a for a in AGGS]
    return names


def _base(state, X):
    cfg = state["cfg"]
    n = len(X)
    d = {}
    for c in CATS:
        lv = state["levels"][c]
        d[c] = np.array([lv.get(v, np.nan) for v in X[c].tolist()], dtype=np.float64)
    for c in NUMS:
        d[c] = X[c].to_numpy(dtype=np.float64)
    if cfg["eng"]:
        d["viol_sum"] = (d["prior_hpv_count"] + d["prior_formal_actions_3y"] + d["prior_stack_test_failures_3y"]
                         + d["prior_tv_deviations_3y"])
        d["pen_per_action"] = d["prior_penalties_3y"] / np.maximum(d["prior_formal_actions_3y"], 1.0)
        d["poll_per_prog"] = d["pollutant_count"] / np.maximum(d["program_count"], 1.0)
        d["hpv_recency"] = d["prior_hpv_count"] / (1.0 + np.nan_to_num(d["days_since_hpv_resolution"], nan=1e9) / 365.0)
        d["eval_recency"] = d["prior_evaluations_3y"] / (1.0 + np.nan_to_num(d["days_since_last_evaluation"], nan=1e9) / 365.0)
    return d


def _matrix(state, d, te_cols):
    names = state["names"]
    cols = [te_cols[c] if c in te_cols else d[c] for c in names]
    edges = state.get("edges", {})
    for i, c in enumerate(names):
        if c in edges:  # learned quantile buckets; missing stays missing
            v = np.asarray(cols[i], dtype=np.float64)
            cols[i] = np.where(np.isnan(v), np.nan, np.searchsorted(edges[c], v, side="right"))
    return np.column_stack(cols).astype(np.float32).reshape(len(cols[0]), len(names))


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    X_train = X_train.reset_index(drop=True)
    y = np.asarray(y_train).astype(float)
    n = len(y)
    levels = {c: {v: i for i, v in enumerate(sorted(X_train[c].dropna().unique()))} for c in CATS}
    names = [c for c in _names(cfg) if c not in cfg["drop"]]
    state = {"levels": levels, "cfg": cfg, "names": names, "te": {}, "edges": {}, "prior": float(y.mean())}
    d = _base(state, X_train)
    te_cols = {}
    if cfg["te"]:
        rng = np.random.RandomState(seed)
        nb = cfg["te_folds"]
        if cfg.get("te_mode", "kfold") == "ordered":
            # Block-ordered encoding: rows in block b are encoded from blocks < b only (training row order).
            # Never uses a row's own label; block 0 has no history and is left missing.
            fold = (np.arange(n) * nb) // n
        else:
            fold = rng.permutation(n) % nb
        for k in TE_KEYS:
            name = "te_" + "_".join(k)
            keys = np.array(_keys(X_train, k), dtype=object)
            oof = np.full(n, np.nan)
            for f in range(nb):
                a = (fold < f) if cfg.get("te_mode", "kfold") == "ordered" else (fold != f)
                if not a.any():
                    continue
                pri = float(y[a].mean())  # prior excludes the encoded block's labels
                tab = _te_table(keys[a], y[a], pri, cfg["te_m"])
                oof[fold == f] = [tab.get(v, pri) for v in keys[fold == f]]
            te_cols[name] = oof
            state["te"][name] = _te_table(keys, y, state["prior"], cfg["te_m"])
    if cfg.get("qbins"):
        Z0 = _matrix(state, d, te_cols)
        for c, nb in cfg["qbins"].items():
            if c in names and c not in CATS:
                v = Z0[:, names.index(c)].astype(np.float64)
                state["edges"][c] = np.unique(np.nanquantile(v, np.linspace(0, 1, nb + 1)[1:-1]))
    for c, e in (cfg.get("fixed_edges") or {}).items():
        if c in names:
            state["edges"][c] = np.asarray(e, dtype=np.float64)
    if cfg.get("agg"):
        g = _agg_frame(X_train).groupby("state")[AGGS].mean()
        state["agg"] = {a: g[a].to_dict() for a in AGGS}
        state["agg_default"] = {a: float(_agg_frame(X_train)[a].mean()) for a in AGGS}
        for a in AGGS:
            te_cols["sa_" + a] = np.array([state["agg"][a].get(v, state["agg_default"][a])
                                           for v in _col(X_train, "state")], dtype=np.float64)
    Z = _matrix(state, d, te_cols)
    ft = ["c" if (c in CATS and cfg["cat_mode"] == "native") else "q" for c in names]
    extra = {}
    if cfg["mono"]:
        extra["monotone_constraints"] = "(" + ",".join("1" if c in MONO_UP else "0" for c in names) + ")"
    kw = {"tree_method": "hist"}
    kw.update(PARAMS)
    kw.update(extra)
    m = xgb.XGBClassifier(enable_categorical=True, feature_types=ft, random_state=seed, n_jobs=threads, **kw)
    m.fit(Z, y_train)
    state["model"] = m
    return state


def prepare(state, X):
    d = _base(state, X)
    te_cols = {}
    for k in TE_KEYS:
        name = "te_" + "_".join(k)
        if name in state["te"]:
            tab = state["te"][name]
            te_cols[name] = np.array([tab.get(v, state["prior"]) for v in _keys(X, k)], dtype=np.float64)
    if state.get("agg"):
        keys = _col(X, "state")
        for a in AGGS:
            te_cols["sa_" + a] = np.array([state["agg"][a].get(v, state["agg_default"][a]) for v in keys],
                                          dtype=np.float64)
    return _matrix(state, d, te_cols)
