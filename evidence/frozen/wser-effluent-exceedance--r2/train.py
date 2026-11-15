"""Self-contained XGBoost solution. Change this file; use evaluate.py to test.

Design (see LOG.md / REPORT.md):
- Only the 15 released predictor columns are used; no IDs, dates or targets.
- Native XGBoost categoricals with levels learned on the fitting partition.
- Shallow, slow, subsampled boosting (the scaffold's depth-6 trees overfit 8k rows).
- Monotone-increasing constraints on the four "worse history => more risk"
  features; this is prior knowledge, not something tuned per level.
- Missing effluent volume means two different things: no prior-year report at all
  (periods == 0), or a report filed in a format without the volume field (e.g. the
  Quebec equivalency rows). The second case gets the sentinel -1 so that NaN keeps
  a single meaning. Row-wise rule, no fitted state.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {"n_estimators": 800, "max_depth": 2, "learning_rate": 0.02, "subsample": 0.7,
          "colsample_bytree": 0.6, "min_child_weight": 10, "reg_lambda": 5}
CATS = ["reporting_frequency", "system_type", "owner_type_operator_type", "province",
        "treatment_family", "receiving_water_type"]
MONO_UP = ["prior_year_exceedance", "prior_year_worst_margin", "ever_exceeded_before",
           "prior_year_acute_lethality_failures"]
VOLUME, PERIODS = "avg_daily_effluent_volume_m3", "periods_reported_prior_year"
# Sensitivity switch: predictors to ignore (e.g. the current-vintage identification attributes).
DROP = []


def prepare(state, X):
    out = {}
    for c in state["num"]:
        out[c] = pd.to_numeric(X[c], errors="coerce").astype(float).to_numpy()
    out = pd.DataFrame(out, index=X.index)
    if VOLUME in out.columns and PERIODS in out.columns:
        v = out[VOLUME].to_numpy().copy()
        v[np.isnan(v) & (out[PERIODS].to_numpy() > 0)] = -1.0
        out[VOLUME] = v
    for c in state["cats"]:
        out[c] = pd.Categorical(X[c], categories=state["levels"][c])
    return out


def fit(X_train, y_train, *, seed, threads):
    cats = [c for c in CATS if c in X_train.columns and c not in DROP]
    num = [c for c in X_train.columns if c not in CATS and c not in DROP]
    levels = {c: pd.Index(sorted(X_train[c].dropna().unique())) for c in cats}
    state = {"num": num, "cats": cats, "levels": levels}
    Z = prepare(state, X_train)
    mono = {c: (1 if c in MONO_UP else 0) for c in Z.columns}
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, random_state=seed,
                          n_jobs=threads, monotone_constraints=mono, **PARAMS)
    m.fit(Z, np.asarray(y_train))
    state["model"] = m
    return state
