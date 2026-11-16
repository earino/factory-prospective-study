"""Self-contained XGBoost solution for eia861-reliability-deterioration.

Features are stateless per-row transforms of the 12 permitted predictors (no identifiers, no
dates, no targets, no cross-row statistics). The label is "next SAIDI >= 1.5 x median of the three
lags", so the model is given the lag levels on a log scale plus ratio/volatility summaries of the
three lags, CAIDI, customers and a municipal-ownership flag. State, reporting standard and the
SAIFI / with-MED columns were removed by training-only ablation (utility-grouped and
leave-one-year-out CV); COLS selects the features actually passed to the model.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = dict(n_estimators=200, max_depth=2, learning_rate=0.03, subsample=0.8, colsample_bytree=0.7,
              min_child_weight=5, reg_lambda=5.0)
OWN = ["Cooperative", "Investor Owned", "Municipal", "Political Subdivision", "State"]
EPS = 1.0  # minutes; stabilises ratios for near-zero SAIDI
COLS = ["lmed", "lmin", "r_max_med", "r_max_min", "r_l1_med", "lcust", "own_2", "lcaidi"]


def _features(X):
    g = lambda c: pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float)
    l1, l2, l3 = g("saidi_nomed_lag1"), g("saidi_nomed_lag2"), g("saidi_nomed_lag3")
    ca, cu = g("caidi_nomed_lag1"), g("customers_lag1")
    L = np.stack([l1, l2, l3], 1)
    med = np.median(L, 1); mx = L.max(1); mn = L.min(1); mean = L.mean(1)
    lg = np.log1p(L)
    f = {}
    f["l1"], f["l3"] = lg[:, 0], lg[:, 2]
    f["lmed"] = np.log1p(med); f["lmin"] = np.log1p(mn)
    f["r_max_med"] = np.log((mx + EPS) / (med + EPS))
    f["r_min_med"] = np.log((mn + EPS) / (med + EPS))
    f["r_max_min"] = np.log((mx + EPS) / (mn + EPS))
    f["r_l1_med"] = np.log((l1 + EPS) / (med + EPS))
    f["r_l1_l2"] = np.log((l1 + EPS) / (l2 + EPS))
    f["r_l2_l3"] = np.log((l2 + EPS) / (l3 + EPS))
    f["lstd"] = lg.std(1)
    f["thr_gap"] = np.log((1.5 * med + EPS) / (mean + EPS))
    f["n_above"] = (L >= 1.5 * med[:, None]).sum(1).astype(float)
    f["l1_pos"] = (l1 == mx) * 2.0 + (l1 == mn) * 1.0
    f["lcaidi"] = np.log1p(ca)
    f["lcust"] = np.log10(cu)
    f["frac_int"] = (L % 1 == 0).mean(1)
    f["ieee"] = (X["reporting_standard"].to_numpy() == "IEEE").astype(float)
    own = X["ownership_code"].to_numpy()
    for i, o in enumerate(OWN):
        f["own_%d" % i] = (own == o).astype(float)
    return pd.DataFrame(f)


def fit(X_train, y_train, *, seed, threads):
    state = {"cols": list(COLS)}
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, **PARAMS)
    m.fit(_features(X_train)[state["cols"]], y_train)
    state["model"] = m
    return state


def prepare(state, X):
    return _features(X)[state["cols"]]
