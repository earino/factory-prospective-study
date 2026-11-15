"""Self-contained XGBoost solution. Change this file; use evaluate.py to test.

One regularized XGBClassifier on the 14 released predictors plus row-local engineered features
and training-derived, label-free primacy-agency descriptors. No target encoding, no identifiers,
no date inputs. prepare() is row-independent: every output row depends only on that input row
and the fitted state.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {"n_estimators": 400, "max_depth": 5, "learning_rate": 0.03, "min_child_weight": 10,
          "subsample": 0.8, "colsample_bytree": 0.7, "reg_lambda": 5}
ENG = ["prev", "sched", "prec", "agstat"]   # engineered feature groups (ablation switches)
NUM = ["prior_pb90_mg_l", "prior_cu90_mg_l", "pb90_change_from_previous", "n_prior_periods_observed",
       "ever_exceeded_before", "population_served_count", "prior_lcr_violations_count", "prior_lslr_milestone"]
N_CAP = 10.0  # cap on the prior-period count: larger counts are rare in training and grow with calendar time
DAYS_PER_MONTH = 30.4375
# prior_pb90_ratio_to_al is prior_pb90_mg_l / 0.015 exactly, so it is omitted.
CATS = ["primary_source_code", "owner_type_code", "primacy_agency_code"]
AGENCY = "primacy_agency_code"
AL = 0.015  # lead action level, mg/L


def _features(state, X):
    eng = state["eng"]
    f = {c: X[c].to_numpy(dtype=float) for c in NUM}
    pb, ch = f["prior_pb90_mg_l"], f["pb90_change_from_previous"]
    gap = X["gap_days_between_periods"].to_numpy(dtype=float)
    plen = X["prior_period_length_days"].to_numpy(dtype=float)
    npri = f["n_prior_periods_observed"]
    f["n_prior_periods_observed"] = np.minimum(npri, N_CAP)
    if "prev" in eng:  # the lead result before the prior one, and two-period summaries
        prev = pb - ch
        f["prev_pb90"] = prev
        f["max2_pb90"] = np.where(np.isnan(prev), pb, np.maximum(pb, prev))
        f["mean2_pb90"] = np.where(np.isnan(prev), pb, (pb + prev) / 2)
        f["n_exceed2"] = (pb > AL).astype(float) + (np.nan_to_num(prev, nan=0.0) > AL)
    if "sched" in eng:  # violation intensity per observed period
        f["viol_per_period"] = f["prior_lcr_violations_count"] / np.maximum(npri, 1.0)
    if "prec" in eng:  # reporting precision / unit artefacts of the prior lead value
        ug = pb * 1000.0
        f["pb_is_zero"] = (pb == 0).astype(float)
        f["pb_frac_ug"] = np.round(ug - np.floor(ug + 1e-9), 4)
        f["pb_int_ug"] = (np.abs(ug - np.round(ug)) < 1e-6).astype(float)
        f["pb_half_ug"] = (np.abs(ug * 2 - np.round(ug * 2)) < 1e-6).astype(float)
        f["pb_unit_suspect"] = (pb >= 1.0).astype(float)
    # Month-rounded schedule lengths replace the raw day counts: leap-day artefacts (364 vs 365, 1094 vs 1095)
    # otherwise act as calendar-year proxies. cycle = prior period length + gap to the target period start.
    f["plen_months"] = np.round(plen / DAYS_PER_MONTH)
    f["cycle_months"] = np.round((gap + plen) / DAYS_PER_MONTH)
    for c in CATS:  # category codes; unseen or missing levels become NaN
        mp = state["maps"][c]
        f[c] = np.array([mp.get(v, np.nan) for v in X[c].to_numpy(dtype=object)], dtype=float)
    if "agstat" in eng:  # label-free agency reporting-practice descriptors learned from training predictors
        ag = X[AGENCY].to_numpy(dtype=object)
        for k, mp in state["agstat"].items():
            f[k] = np.array([mp.get(v, np.nan) for v in ag], dtype=float)
    return f


def prepare(state, X):
    f = _features(state, X)
    return np.column_stack([f[c] for c in state["cols"]])


def fit(X_train, y_train, *, seed, threads):
    y = np.asarray(y_train).astype(int)
    state = {"eng": list(ENG), "maps": {}, "agstat": {}}
    for c in CATS:
        state["maps"][c] = {v: float(i) for i, v in enumerate(sorted(X_train[c].dropna().unique()))}
    if "agstat" in ENG:
        a, pb = X_train[AGENCY], X_train["prior_pb90_mg_l"]
        g = X_train.groupby(AGENCY)
        state["agstat"] = {
            "ag_zero_share": (pb == 0).groupby(a).mean().to_dict(),
            "ag_med_pb": g["prior_pb90_mg_l"].median().to_dict(),
            "ag_exc_share": (pb > AL).groupby(a).mean().to_dict(),
            "ag_med_len": g["prior_period_length_days"].median().to_dict(),
            "ag_cu_share": X_train["prior_cu90_mg_l"].notna().groupby(a).mean().to_dict(),
        }
    f = _features(state, X_train)
    cols = list(f)
    state["cols"] = cols
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True,
                          feature_types=["c" if c in CATS else "q" for c in cols],
                          random_state=seed, n_jobs=threads, **PARAMS)
    m.fit(np.column_stack([f[c] for c in cols]), y)
    state["model"] = m
    return state
