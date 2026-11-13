"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

# Feature groups are switchable so ablations are one-line changes.
CONFIG = {
    "groups": ["penalty", "region", "ratios"],
    "monotone_penalty": True,
    "recency_power": 8.0,  # weight = ((i+1)/n)**power over training row order; 0 disables
    "time_feature": False,  # training-order index as a feature; scoring rows are placed at the end (1.0)
    "mono_extra": {"log_penalty_per_reg": 1, "log_penalty_per_cat": 1},  # extra monotone constraints {feature: +1/-1}
    "te_prior": 10.0,  # smoothing strength (pseudo-rows) for region target encoding
    "te_folds": 5,  # out-of-fold encoding for training rows
    "params": {
        "n_estimators": 150,
        "max_depth": 2,
        "learning_rate": 0.03,
        "subsample": 1.0,
        "colsample_bynode": 1.0,
        "min_child_weight": 5,
        "reg_lambda": 5.0,
        "gamma": 0.0,
    },
}

ACTION_TOKENS = ["CO", "CO/CP", "CP", "LOC", "NOA", "WI"]
REGIONS = ["Central", "Eastern", "Southern", "Southwest", "Western"]
ROUTES = ["Construction", "Failure Investigation", "First Operating", "Integrated", "Specialized"]


def _num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return np.nan
    return v


def _row_features(row, groups):
    """Stateless per-row features from the nine contract predictors."""
    f = {}
    p = _num(row.get("proposed_penalty_usd"))
    vc = _num(row.get("violation_category_count"))
    rc = _num(row.get("cited_regulation_count"))
    lp = np.log10(p) if p == p and p > 0 else np.nan
    if "penalty" in groups:
        f["log_penalty"] = lp
    if "counts" in groups:
        f["violation_category_count"] = vc
        f["cited_regulation_count"] = rc
    if "ratios" in groups:
        f["log_penalty_per_reg"] = lp - np.log10(rc) if rc == rc and rc > 0 else np.nan
        f["log_penalty_per_cat"] = lp - np.log10(vc) if vc == vc and vc > 0 else np.nan
    if "flags" in groups:
        f["integrity_management_flag"] = _num(row.get("integrity_management_flag"))
        pco = _num(row.get("proposed_compliance_order"))
        f["proposed_compliance_order"] = 0.0 if pco != pco else pco
    if "actions" in groups:
        na = row.get("notice_actions")
        toks = set(t.strip() for t in na.split(",")) if isinstance(na, str) else set()
        for t in ACTION_TOKENS:
            f["act_" + t] = float(t in toks)
        f["act_n"] = float(len(toks))
    if "ptype" in groups:
        pt = row.get("pipeline_type")
        pt = pt.upper() if isinstance(pt, str) else ""
        f["pt_gas"] = float(pt.startswith("GAS"))
        f["pt_lng"] = float("LNG" in pt)
        f["pt_intrastate"] = float("INTRASTATE" in pt)
        f["pt_offshore"] = float("OFFSHORE" in pt)
    if "region" in groups:
        rg = row.get("region")
        for r in REGIONS:
            f["region_" + r] = float(rg == r)
    if "route" in groups:
        dr = row.get("discovery_route")
        for r in ROUTES:
            f["route_" + r] = float(dr == r)
    if "lng" in groups:
        pt = row.get("pipeline_type")
        f["pt_lng"] = float(isinstance(pt, str) and "LNG" in pt.upper())
    if "specialized" in groups:
        f["route_Specialized"] = float(row.get("discovery_route") == "Specialized")
    if "round" in groups:
        f["round_1k"] = float(p == p and p % 1000 == 0)
    return f


def _matrix(X, groups, cols=None):
    recs = [_row_features(r, groups) for r in X.to_dict("records")]
    out = pd.DataFrame.from_records(recs, columns=cols).astype(np.float32)
    return out


def _te_table(reg, y, prior_m):
    """Smoothed positive rate per region level from the given rows only."""
    reg = np.asarray(reg, dtype=object)
    y = np.asarray(y, dtype=float)
    g = float(y.mean()) if len(y) else 0.5
    tab = {}
    for r in REGIONS:
        m = reg == r
        tab[r] = float((y[m].sum() + prior_m * g) / (m.sum() + prior_m))
    return {"global": g, "levels": tab}


def _te_apply(tab, reg):
    return np.array([tab["levels"].get(r, tab["global"]) for r in reg], dtype=np.float32)


def fit(X_train, y_train, *, seed, threads):
    cfg = CONFIG
    groups = list(cfg["groups"])
    y_train = np.asarray(y_train)
    n = len(X_train)
    Z = _matrix(X_train, [g for g in groups if g != "region_te"])
    te = None
    if "region_te" in groups:
        reg = X_train["region"].to_numpy(dtype=object)
        # Out-of-fold: each training row is encoded from folds that exclude its own label
        # (prior included). Scoring rows use the table fitted on all training rows.
        k = int(cfg["te_folds"])
        fold = np.random.RandomState(seed).permutation(n) % k
        col = np.zeros(n, dtype=np.float32)
        for j in range(k):
            inn = fold != j
            col[~inn] = _te_apply(_te_table(reg[inn], y_train[inn], cfg["te_prior"]), reg[~inn])
        Z["region_te"] = col
        te = _te_table(reg, y_train, cfg["te_prior"])
    if cfg.get("time_feature"):
        Z["t_order"] = ((np.arange(n) + 1.0) / n).astype(np.float32)
    cols = list(Z.columns)
    params = dict(cfg["params"])
    mono = {}
    if cfg.get("monotone_penalty"):
        mono.update({c: 1 for c in cols if c in ("log_penalty", "region_te")})
    mono.update({c: int(v) for c, v in cfg.get("mono_extra", {}).items() if c in cols})
    if mono:
        params["monotone_constraints"] = mono
    w = None
    if cfg.get("recency_power", 0):
        # Training rows arrive in release (chronological) order; later rows weigh more.
        w = ((np.arange(n) + 1.0) / n) ** cfg["recency_power"]
        w = w / w.mean()
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, **params)
    m.fit(Z, y_train, sample_weight=w)
    return {"cols": cols, "groups": groups, "te": te, "model": m}


def prepare(state, X):
    Z = _matrix(X, [g for g in state["groups"] if g != "region_te"])
    if state.get("te") is not None:
        Z["region_te"] = _te_apply(state["te"], X["region"].to_numpy(dtype=object))
    if "t_order" in state["cols"]:
        Z["t_order"] = np.float32(1.0)
    return Z[state["cols"]]


def predict(model, X):
    return model["model"].predict_proba(prepare(model, X))[:, 1]
