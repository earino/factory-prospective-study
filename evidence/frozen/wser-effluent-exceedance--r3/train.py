"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    "drop": [],                 # raw declared features to remove
    "extra": ["period_gap"],                # engineered feature groups to add
    "cat_mode": "native",       # native | ordinal | onehot
    "te": [],                   # list of tuples of columns for out-of-fold target encoding
    "te_smooth": 20.0,
    "w_nohist": 1.0,            # training weight of rows without limit-based history
    "mono": {"prior_year_exceedance": 1, "prior_year_worst_margin": 1, "ever_exceeded_before": 1,
             "prior_year_acute_lethality_failures": 1},   # feature -> +1/-1
    "qc_mask": True,
    # history features may interact only with each other (+ shared province/treatment); static features likewise
    "ic": [["prior_year_exceedance", "prior_year_worst_margin", "ever_exceeded_before", "history_years_reported"]],
    "ic_shared": ["province", "treatment_family"],
    "params": {"n_estimators": 800, "max_depth": 3, "learning_rate": 0.015, "min_child_weight": 20,
               "subsample": 0.7, "colsample_bytree": 0.5, "reg_lambda": 5},
}
CATS = ["reporting_frequency", "system_type", "owner_type_operator_type", "province", "treatment_family",
        "receiving_water_type"]


def _key(X, cols):
    k = X[cols[0]].astype(object).where(X[cols[0]].notna(), "NA").astype(str)
    for c in cols[1:]:
        k = k + "|" + X[c].astype(object).where(X[c].notna(), "NA").astype(str)
    return k


def _base(state, X):
    cfg = state["cfg"]
    out = {}
    if cfg.get("qc_mask"):
        # Quebec stopped reporting system type from 2019 (equivalency agreement); harmonize all Quebec rows.
        X = X.copy()
        X["system_type"] = X["system_type"].where(X["province"] != "Quebec", np.nan)
    for c in state["raw"]:
        if c in CATS:
            if cfg["cat_mode"] == "native":
                out[c] = pd.Categorical(X[c], categories=state["levels"][c])
            elif cfg["cat_mode"] == "ordinal":
                out[c] = X[c].map(state["ordmap"][c]).astype(float)
            else:
                for lv in state["levels"][c]:
                    out[c + "=" + str(lv).replace("<", "lt").replace(">", "gt").replace("[", "(").replace("]", ")")] = (X[c] == lv).astype(float)
        else:
            out[c] = X[c].astype(float)
    ex = cfg["extra"]
    pe = X["prior_year_exceedance"]; ee = X["ever_exceeded_before"]; mg = X["prior_year_worst_margin"]
    per = X["periods_reported_prior_year"].astype(float)
    if "hist_state" in ex:
        # 0 never exceeded, 1 exceeded earlier but not last year, 2 exceeded last year, nan none
        s = pd.Series(np.nan, index=X.index)
        s = s.mask(ee == 0, 0.0).mask((ee == 1) & (pe != 1), 1.0).mask(pe == 1, 2.0)
        out["hist_state"] = s
    if "new_system" in ex:
        out["new_system"] = (X["history_years_reported"] <= 1).astype(float)
    if "hist_cap" in ex:
        out["hist_cap"] = X["history_years_reported"].clip(upper=cfg.get("hist_cap", 3)).astype(float)
    if "period_gap" in ex:
        exp = X["reporting_frequency"].map({"annual": 1.0, "quarterly": 4.0, "monthly": 12.0})
        out["period_short"] = (per < exp).astype(float).where(exp.notna(), np.nan)
        out["monthly_like"] = (per >= 11).astype(float)
    if "acute_any" in ex:
        a = X["prior_year_acute_lethality_failures"]
        out["acute_tested"] = a.notna().astype(float)
    if "n_missing" in ex:
        out["n_missing"] = X[["system_type", "avg_daily_effluent_volume_m3", "owner_type_operator_type",
                              "hydraulic_retention_ge_5_days", "receiving_water_type"]].isna().sum(axis=1).astype(float)
    if "log_margin" in ex:
        out["margin_score"] = np.log1p(mg.fillna(0.0)) + ee.fillna(0.0) * 0.5
    return pd.DataFrame(out, index=X.index)


def _te_apply(table, prior, smooth, keys):
    s = keys.map(table["s"]).fillna(0.0).to_numpy(dtype=float)
    n = keys.map(table["n"]).fillna(0.0).to_numpy(dtype=float)
    return (s + prior * smooth) / (n + smooth)


def fit(X_train, y_train, *, seed, threads):
    cfg = {k: (dict(v) if isinstance(v, dict) else (list(v) if isinstance(v, list) else v)) for k, v in CFG.items()}
    X = X_train.reset_index(drop=True)
    y = np.asarray(y_train).astype(int)
    raw = [c for c in X.columns if c not in cfg["drop"]]
    levels = {c: [str(v) for v in sorted(X[c].dropna().unique())] for c in CATS}
    state = {"cfg": cfg, "raw": raw, "levels": levels, "te_tables": {}, "prior": float(y.mean())}
    state["ordmap"] = {c: {lv: float(i) for i, lv in enumerate(levels[c])} for c in CATS}
    F = _base(state, X)
    # Out-of-fold target encoding: each training row's encoding (incl. the prior) excludes its own fold's labels.
    if cfg["te"]:
        rng = np.random.RandomState(seed)
        fold = rng.randint(0, 5, size=len(X))
        for cols in cfg["te"]:
            name = "te_" + "_x_".join(cols)
            keys = _key(X, list(cols))
            enc = np.zeros(len(X))
            for f in range(5):
                tr = fold != f
                g = pd.DataFrame({"k": keys[tr], "y": y[tr]}).groupby("k")["y"].agg(["sum", "count"])
                tab = {"s": g["sum"].to_dict(), "n": g["count"].to_dict()}
                enc[~tr] = _te_apply(tab, float(y[tr].mean()), cfg["te_smooth"], keys[~tr])
            F[name] = enc
            g = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
            state["te_tables"][tuple(cols)] = {"s": g["sum"].to_dict(), "n": g["count"].to_dict()}
    state["columns"] = list(F.columns)
    w = np.where(X["prior_year_exceedance"].isna().to_numpy(), cfg["w_nohist"], 1.0)
    params = dict(cfg["params"])
    if cfg["mono"]:
        params["monotone_constraints"] = {c: int(cfg["mono"].get(c, 0)) for c in state["columns"] if c in cfg["mono"]}
    if cfg.get("ic"):
        # Interaction constraints: listed groups may interact internally; all remaining features form one more group.
        groups = [[c for c in g if c in state["columns"]] for g in cfg["ic"]]
        used = {c for g in groups for c in g}
        rest = [c for c in state["columns"] if c not in used]
        shared = [c for c in cfg.get("ic_shared", []) if c in state["columns"]]
        groups = [g + [c for c in shared if c not in g] for g in groups + [rest] if g]
        params["interaction_constraints"] = groups
    model = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, random_state=seed, n_jobs=threads, **params)
    keep = w > 0
    model.fit(F[keep], y[keep], sample_weight=w[keep])
    state["model"] = model
    return state


def prepare(state, X):
    F = _base(state, X)
    for cols, tab in state["te_tables"].items():
        F["te_" + "_x_".join(cols)] = _te_apply(tab, state["prior"], state["cfg"]["te_smooth"], _key(X, list(cols)))
    return F[state["columns"]]
