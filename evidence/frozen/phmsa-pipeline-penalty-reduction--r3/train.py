"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

# Single configuration block; diagnostics (diag/cv.py) override entries of CFG.
CFG = {
    "features": ["log_pen", "reg_Eastern", "reg_Southern", "reg_Southwest"],          # ordered list of engineered feature names
    "monotone": {"log_pen": 1},      # monotone constraints by feature name
    "route_weight": 1.0,             # training weight multiplier for discovery_route == "First Operating"
    "te": {},                        # raw categorical column -> smoothing m; adds feature "te_<col>" (out-of-fold in fit)
    "te_folds": 5,
    "round_weight": 0.3,             # training weight for rows whose penalty is a round $1,000 multiple
    "params": {"n_estimators": 100, "max_depth": 2, "learning_rate": 0.1,
               "subsample": 1.0, "colsample_bytree": 1.0, "min_child_weight": 5,
               "reg_lambda": 1.0, "gamma": 0.0},
}

ACTION_TOKENS = ["CO", "CP", "CO/CP", "WI", "LOC", "NOA"]
REGIONS = ["Central", "Eastern", "Southern", "Southwest", "Western"]
ROUTES = ["First Operating", "Failure Investigation", "Integrated", "Specialized", "Construction"]


def _engineer(X):
    """Row-local feature engineering: every value depends on that row only."""
    out = pd.DataFrame(index=X.index)
    pen = pd.to_numeric(X["proposed_penalty_usd"], errors="coerce").astype(float)
    ncat = pd.to_numeric(X["violation_category_count"], errors="coerce").astype(float)
    nreg = pd.to_numeric(X["cited_regulation_count"], errors="coerce").astype(float)
    out["log_pen"] = np.log10(pen.clip(lower=1.0))
    out["n_cat"] = ncat
    out["n_reg"] = nreg
    out["log_pen_per_reg"] = np.log10((pen / nreg.clip(lower=1.0)).clip(lower=1.0))
    out["log_pen_per_cat"] = np.log10((pen / ncat.clip(lower=1.0)).clip(lower=1.0))
    out["reg_per_cat"] = nreg / ncat.clip(lower=1.0)
    out["im_flag"] = pd.to_numeric(X["integrity_management_flag"], errors="coerce").astype(float)
    out["comp_order"] = pd.to_numeric(X["proposed_compliance_order"], errors="coerce").fillna(0.0).astype(float)
    out["round_1k"] = (pen % 1000 == 0).astype(float)
    out["round_100"] = (pen % 100 == 0).astype(float)
    acts = X["notice_actions"].fillna("").astype(str).map(lambda s: [t.strip() for t in s.split(",") if t.strip()])
    for t in ACTION_TOKENS:
        out["act_" + t.replace("/", "")] = acts.map(lambda a, t=t: float(t in a))
    out["n_act"] = acts.map(len).astype(float)
    out["cp_only"] = acts.map(lambda a: float(a == ["CP"]))
    pt = X["pipeline_type"].fillna("").astype(str).str.upper()
    out["pt_gas"] = pt.str.contains("GAS").astype(float)
    out["pt_liquid"] = pt.str.contains("LIQUID").astype(float)
    out["pt_lng"] = pt.str.contains("LNG").astype(float)
    out["pt_intrastate"] = pt.str.contains("INTRASTATE").astype(float)
    out["pt_offshore"] = pt.str.contains("OFFSHORE").astype(float)
    rg = X["region"].fillna("").astype(str)
    for r in REGIONS:
        out["reg_" + r] = (rg == r).astype(float)
    dr = X["discovery_route"].fillna("").astype(str)
    for r in ROUTES:
        out["route_" + r.replace(" ", "_")] = (dr == r).astype(float)
    return out


def _te_map(keys, y, m, prior):
    g = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    return ((g["sum"] + m * prior) / (g["count"] + m)).to_dict()


def fit(X_train, y_train, *, seed, threads):
    feats = list(CFG["features"])
    y = np.asarray(y_train).astype(float)
    te_cfg = dict(CFG.get("te", {}))
    state = {"features": feats, "te": {}}
    eng = _engineer(X_train)
    Z = eng.copy()
    if te_cfg:
        # Out-of-fold target encoding: a training row's own label never enters its encoding,
        # its prior, or its smoothing. Scoring rows use the full-training map stored in state.
        k = int(CFG.get("te_folds", 5))
        fold = np.random.RandomState(seed).permutation(len(y)) % k
        for col, m in te_cfg.items():
            keys = X_train[col].fillna("").astype(str).to_numpy()
            oof = np.zeros(len(y))
            for f in range(k):
                tr, te = fold != f, fold == f
                prior = y[tr].mean()
                mp = _te_map(keys[tr], y[tr], float(m), prior)
                oof[te] = [mp.get(v, prior) for v in keys[te]]
            Z["te_" + col] = oof
            prior = y.mean()
            state["te"][col] = {"map": _te_map(keys, y, float(m), prior), "prior": float(prior)}
    mono = tuple(int(CFG.get("monotone", {}).get(f, 0)) for f in feats)
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads,
                          monotone_constraints=mono, **CFG["params"])
    w = np.where(eng["round_1k"].to_numpy() == 1.0, float(CFG.get("round_weight", 1.0)), 1.0)
    w = w * np.where(eng["route_First_Operating"].to_numpy() == 1.0, float(CFG.get("route_weight", 1.0)), 1.0)
    m.fit(Z[feats].astype("float32"), y.astype(int), sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    Z = _engineer(X)
    for col, enc in state.get("te", {}).items():
        keys = X[col].fillna("").astype(str)
        Z["te_" + col] = keys.map(lambda v, enc=enc: enc["map"].get(v, enc["prior"])).astype(float)
    return Z[state["features"]].astype("float32")
