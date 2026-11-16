"""Self-contained XGBoost solution for EIA-861 day-to-day reliability deterioration.

The label is "next-year SAIDI (excl. major event days) >= 1.5 x median of the three lagged
values", i.e. a relative jump against the utility's own baseline.  Raw levels are therefore
re-expressed as (a) the log baseline, (b) how far the latest year already sits from the
1.5x-median threshold, (c) the spread of the three lags around their median, and (d) system
size / event-count proxies (customers, customer-minutes, customer-interruptions, CAIDI) that
govern how easily a small system's index moves by 50%.

All 10 features are deterministic functions of one row.  No target encoding, no state,
ownership or reporting-standard inputs (they added nothing once size and level were present),
and no learned preprocessing state beyond the column list.

Seven features carry monotone constraints that encode the mechanics of a relative-jump label:
risk falls with the baseline level, with the headroom between the latest year and the
threshold, and with system size / interruption counts; it rises with upside spread, with the
skew of the lags above their median, and with CAIDI at a given level (fewer, longer
interruptions).  With ~430 positives the constraints act as a prior, not a fit to validation.

SAIFI including major event days was dropped as a direct input: over bootstrap resamples of the
training utilities its removal improved a training-only forward split (fit 2016-17, score
2019), and its sign was not stable between eras.  It still enters through major-event CAIDI.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

# colsample 0.5 / 250 trees: the inputs are strongly correlated (level, customer-minutes,
# customer-interruptions, customers), and stronger per-tree column subsampling was ahead of
# 0.8 / 300 on all five training-only cohort splits under bootstrap resampling.
PARAMS = {"n_estimators": 250, "max_depth": 2, "learning_rate": 0.03, "subsample": 0.8,
          "colsample_bytree": 0.5, "min_child_weight": 5, "reg_lambda": 5.0}
COLS = ["lcaidi", "lcust", "lmed", "mean_med", "gap", "lint", "lcustmin",
        "t_up", "t_down", "med_caidi"]
MONO = {"lmed": -1, "gap": -1, "t_up": 1, "lint": -1, "lcustmin": -1, "mean_med": 1, "lcaidi": 1}


def _num(X, c):
    return pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float)


def _features(X):
    l1 = _num(X, "saidi_nomed_lag1")
    raw = np.stack([l1, _num(X, "saidi_nomed_lag2"), _num(X, "saidi_nomed_lag3")], axis=1)
    med = np.median(raw, axis=1)                      # the label's own baseline
    L = np.log1p(np.clip(raw, 0, None))
    lmed = np.log1p(np.clip(med, 0, None))
    TL = np.log(np.clip(raw, 0.05, None))             # true logs: exact ratios for tiny SAIDI
    tmed = np.log(np.clip(med, 0.05, None))
    wm = _num(X, "saidi_with_med_lag1")
    sf, sfm = _num(X, "saifi_nomed_lag1"), _num(X, "saifi_with_med_lag1")
    lcu = np.log(np.clip(_num(X, "customers_lag1"), 1, None))
    f = {
        "lcaidi": np.log1p(_num(X, "caidi_nomed_lag1")),
        "lcust": lcu,
        "lmed": lmed,
        "mean_med": np.log1p(raw.mean(axis=1)) - lmed,          # skew of the 3 lags above baseline
        "gap": np.log1p(1.5 * med) - L[:, 0],                   # latest year vs the threshold
        "lint": lcu + np.log(np.clip(sf, 1e-3, None)),          # log customer-interruptions
        "lcustmin": lcu + lmed,                                 # log customer-minutes at baseline
        "t_up": TL.max(axis=1) - tmed,                          # upside spread around the median
        "t_down": tmed - TL.min(axis=1),                        # downside spread
        "med_caidi": np.log1p(np.clip(wm - l1, 0, None) / np.clip(sfm - sf, 1e-3, None)),  # major-event CAIDI
    }
    return pd.DataFrame(f)[COLS]


def fit(X_train, y_train, *, seed, threads):
    y = np.asarray(y_train).astype(int)
    state = {"cols": list(COLS)}
    mono = "(" + ",".join(str(MONO.get(c, 0)) for c in COLS) + ")"
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads,
                          monotone_constraints=mono, **PARAMS)
    m.fit(prepare(state, X_train), y)
    state["model"] = m
    return state


def prepare(state, X):
    return _features(X)[state["cols"]]
