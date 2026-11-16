"""Self-contained XGBoost solution: additive stumps on seven row-local reliability features.

Every feature is computed from one row's own permitted inputs (three lagged no-MED SAIDI values,
CAIDI lag 1, customer count). Nothing is learned outside the booster: no encoders, imputers, target
statistics, identifiers, dates, state, ownership or reporting standard. Compared with trial f94fb7ed
(ten features) this drops `range` (redundant with max/median and mean/median) and the two columns the
stumps never split on (`own`, `std_other`). The exploratory superset is scratch/train_explore.py.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {"n_estimators": 800, "max_depth": 1, "learning_rate": 0.02, "subsample": 0.85,
          "colsample_bytree": 0.5, "min_child_weight": 10, "reg_lambda": 20.0}
LAGS = ["saidi_nomed_lag1", "saidi_nomed_lag2", "saidi_nomed_lag3"]
OWN = ["Cooperative", "Investor Owned", "Municipal", "Political Subdivision", "State", "Federal"]
FEATURES = ["med", "logcust", "cust_minutes", "max_med", "l1_med", "mean_med", "caidi"]


def fit(X_train, y_train, *, seed, threads):
    state = {"features": list(FEATURES)}
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, **PARAMS)
    m.fit(prepare(state, X_train), np.asarray(y_train))
    state["model"] = m
    return state


def prepare(state, X):
    L = X[LAGS].to_numpy(dtype=float)
    cu = X["customers_lag1"].to_numpy(dtype=float)
    with np.errstate(all="ignore"):
        med = np.nanmedian(L, axis=1)            # the label's own baseline
        mx = np.nanmax(L, axis=1)
        mn = np.nanmin(L, axis=1)
        lmed = np.log1p(med)
        f = {
            "med": med,
            "logcust": np.log10(cu),
            "cust_minutes": np.log1p(med * cu),  # total customer-minutes at the norm
            "max_med": np.log1p(mx) - lmed,      # worst recent year relative to the norm
            "l1_med": np.log1p(L[:, 0]) - lmed,  # latest year relative to the norm
            "range": np.log1p(mx) - np.log1p(mn),
            "mean_med": np.log1p(np.nanmean(L, axis=1)) - lmed,
            "caidi": X["caidi_nomed_lag1"].to_numpy(dtype=float),
            "own": np.array([OWN.index(o) if o in OWN else np.nan for o in X["ownership_code"].to_numpy()], dtype=float),
            "std_other": (X["reporting_standard"].to_numpy() == "OTHER").astype(float),
        }
    return pd.DataFrame(f, index=X.index)[state["features"]].astype(float)


def predict(model, X):
    return model["model"].predict_proba(prepare(model, X))[:, 1]
