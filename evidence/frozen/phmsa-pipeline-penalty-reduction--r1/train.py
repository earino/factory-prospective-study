"""Self-contained XGBoost solution. Change this file; use evaluate.py to test.

All features are functions of a single row's permitted notice-time inputs. No
target encoding, no cross-row statistics, no identifiers, no dates.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

CONFIG = {
    # feature groups to include (see _row_features)
    "groups": ["pen", "region_key", "f:route_Failure Investigation"],
    # monotone constraint on penalty-size features (+1) or none (0)
    "mono_pen": 1,
    # optional extra monotone constraints {feature: +1/-1}
    "mono_extra": {},
    # half-life (in training rows, file order) for recency weights; None = uniform
    "half_life": None,
    "params": {"n_estimators": 1200, "max_depth": 2, "learning_rate": 0.02, "subsample": 0.5, "min_child_weight": 3.49},
}

ACTION_TOKENS = ["CO", "CO/CP", "CP", "LOC", "NOA", "WI"]
REGIONS = ["Central", "Eastern", "Southern", "Southwest", "Western"]
ROUTES = ["Construction", "Failure Investigation", "First Operating", "Integrated", "Specialized"]

GROUPS = {
    "pen": ["log_pen"],
    "pen_ratio": ["log_pen_per_reg", "log_pen_per_cat"],
    "pen_round": ["pen_round_1k"],
    "counts": ["n_cat", "n_reg"],
    "flags": ["im_flag", "compliance_order"],
    "actions": ["act_" + t for t in ACTION_TOKENS] + ["n_actions"],
    "ptype": ["pt_gas", "pt_liquid", "pt_lng", "pt_intrastate", "pt_offshore"],
    "region": ["reg_" + r for r in REGIONS],
    "region_key": ["reg_Eastern", "reg_Southwest"],
    "route": ["route_" + r for r in ROUTES],
}
ALL_FEATURES = sorted({c for g in GROUPS.values() for c in g})
for _c in ALL_FEATURES:
    GROUPS.setdefault("f:" + _c, [_c])
PEN_FEATURES = {"log_pen", "log_pen_per_reg", "log_pen_per_cat"}


def _num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return np.nan
    return v


def _text(v):
    return v.strip() if isinstance(v, str) else ""


def _row_features(X):
    out = pd.DataFrame(index=X.index)
    pen = pd.to_numeric(X["proposed_penalty_usd"], errors="coerce").astype(float)
    n_cat = pd.to_numeric(X["violation_category_count"], errors="coerce").astype(float)
    n_reg = pd.to_numeric(X["cited_regulation_count"], errors="coerce").astype(float)
    out["log_pen"] = np.log10(pen.clip(lower=1.0))
    out["log_pen_per_reg"] = np.log10((pen / n_reg.clip(lower=1.0)).clip(lower=1.0))
    out["log_pen_per_cat"] = np.log10((pen / n_cat.clip(lower=1.0)).clip(lower=1.0))
    out["pen_round_1k"] = (pen % 1000 == 0).astype(float)
    out["n_cat"] = n_cat
    out["n_reg"] = n_reg
    out["im_flag"] = pd.to_numeric(X["integrity_management_flag"], errors="coerce").astype(float)
    out["compliance_order"] = pd.to_numeric(X["proposed_compliance_order"], errors="coerce").fillna(0.0).astype(float)
    toks = [[t.strip() for t in _text(v).split(",") if t.strip()] for v in X["notice_actions"]]
    for t in ACTION_TOKENS:
        out["act_" + t] = [float(t in r) for r in toks]
    out["n_actions"] = [float(len(r)) for r in toks]
    pt = [_text(v).upper() for v in X["pipeline_type"]]
    out["pt_gas"] = [float("GAS" in s) for s in pt]
    out["pt_liquid"] = [float("LIQUID" in s) for s in pt]
    out["pt_lng"] = [float("LNG" in s) for s in pt]
    out["pt_intrastate"] = [float("INTRASTATE" in s) for s in pt]
    out["pt_offshore"] = [float("OFFSHORE" in s) for s in pt]
    reg = [_text(v) for v in X["region"]]
    for r in REGIONS:
        out["reg_" + r] = [float(s == r) for s in reg]
    route = [_text(v) for v in X["discovery_route"]]
    for r in ROUTES:
        out["route_" + r] = [float(s == r) for s in route]
    return out


def fit(X_train, y_train, *, seed, threads):
    cfg = CONFIG
    cols = [c for g in cfg["groups"] for c in GROUPS[g]]
    state = {"cols": cols}
    extra = cfg.get("mono_extra") or {}
    mono = tuple(int(extra[c]) if c in extra else (cfg["mono_pen"] if c in PEN_FEATURES else 0) for c in cols)
    w = None
    if cfg["half_life"]:
        # Training rows are in file (chronological) order; weight later rows more.
        age = (len(X_train) - 1 - np.arange(len(X_train))).astype(float)
        w = 0.5 ** (age / float(cfg["half_life"]))
    kw = {"tree_method": "hist", "monotone_constraints": mono}
    kw.update(cfg["params"])
    m = xgb.XGBClassifier(random_state=seed, n_jobs=threads, **kw)
    m.fit(prepare(state, X_train), y_train, sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    return _row_features(X)[state["cols"]].astype(np.float32)
