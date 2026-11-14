"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {"n_estimators": 300, "max_depth": 4, "learning_rate": 0.01, "subsample": 0.7,
          "colsample_bytree": 0.3, "min_child_weight": 30, "reg_lambda": 10}
# pair_departures_prior_3m is dropped (redundant with competing_carriers_prior_3m; removal was non-negative locally).
# entry_calendar_month is deliberately not used as a model feature (it acts as a training-cohort fingerprint,
# e.g. the January 2012 carrier recodes); it is only part of the training cohort key for weights.
BASE = ["distance_miles", "carrier_departures_prior_12m", "carrier_active_pairs_prior_12m",
        "carrier_route_attrition_prior_12m", "origin_market_departures_prior_12m", "dest_market_departures_prior_12m",
        "competing_carriers_prior_3m", "entry_month_departures",
        "entry_month_seats_per_departure", "entry_month_load_factor", "carrier_new_at_origin", "carrier_new_at_dest"]
EXTRA = ["pax", "seats", "seat_miles", "gravity_dist"]
# Sign constraints from domain priors (not fitted): carriers that recently abandoned more routes discontinue more;
# more first-month passengers and larger aircraft gauge mean less discontinuation.
MONOTONE = {"carrier_route_attrition_prior_12m": 1, "pax": -1, "entry_month_seats_per_departure": -1,
            "entry_month_load_factor": -1, "entry_month_departures": -1, "seats": -1, "seat_miles": -1,
            "gravity_dist": -1}  # larger endpoint markets / shorter distance = more demand potential
# Carrier-level trailing aggregates are identical for all entries of one carrier in one month, so equal values
# mark one carrier-month launch cohort among the TRAINING rows (used only for fitting weights, never at prediction).
CLUSTER_KEY = ["carrier_departures_prior_12m", "carrier_active_pairs_prior_12m", "entry_calendar_month"]
WEIGHT_POWER = 1.0
# Training-only jitter of the carrier-level aggregates: they are exact fingerprints of training cohorts, and carriers
# drift in size/attrition by prediction time. K noisy copies of the training rows are appended to the originals.
JITTER_COPIES = 7
JITTER_ATTRITION_SD = 0.05   # additive, on the attrition share
JITTER_SIZE_SD = 0.4         # multiplicative log-normal, on carrier departures / active pairs


def _cluster_weights(X):
    key = X[CLUSTER_KEY].astype(str).agg("|".join, axis=1)
    n = key.map(key.value_counts()).to_numpy(dtype=float)
    w = n ** (-WEIGHT_POWER)
    return w / w.mean()


def _augment(X, y, w, seed):
    rng = np.random.default_rng(seed)
    Xs, ys, ws = [X], [y], [w]
    for _ in range(JITTER_COPIES):
        Z = X.copy()
        if JITTER_SIZE_SD > 0:
            f = np.exp(rng.normal(0, JITTER_SIZE_SD, len(X)))
            Z["carrier_departures_prior_12m"] = Z["carrier_departures_prior_12m"] * f
            Z["carrier_active_pairs_prior_12m"] = Z["carrier_active_pairs_prior_12m"] * f * np.exp(rng.normal(0, JITTER_SIZE_SD / 2, len(X)))
        a = Z["carrier_route_attrition_prior_12m"].to_numpy(dtype=float)
        Z["carrier_route_attrition_prior_12m"] = np.clip(a + rng.normal(0, JITTER_ATTRITION_SD, len(X)), 0, 1)
        Xs.append(Z); ys.append(y); ws.append(w)
    return pd.concat(Xs, ignore_index=True), np.concatenate(ys), np.concatenate(ws)


def fit(X_train, y_train, *, seed, threads):
    state = {"base": list(BASE)}
    w = _cluster_weights(X_train)
    Xa, ya, wa = _augment(X_train[BASE].astype(float), np.asarray(y_train), w, seed)
    params = dict(PARAMS)
    # keep regularisation per original row constant when rows are replicated
    params["min_child_weight"] = PARAMS["min_child_weight"] * (JITTER_COPIES + 1)
    params["reg_lambda"] = PARAMS["reg_lambda"] * (JITTER_COPIES + 1)
    mono = "(" + ",".join(str(MONOTONE.get(c, 0)) for c in BASE + EXTRA) + ")"
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, monotone_constraints=mono, **params)
    m.fit(prepare(state, Xa), ya, sample_weight=wa)
    state["model"] = m
    return state


def prepare(state, X):
    # Row-wise deterministic transforms only: every output row depends on that input row alone.
    g = lambda c: X[c].to_numpy(dtype=float)
    cols = [g(c) for c in state["base"]]
    seats = g("entry_month_departures") * g("entry_month_seats_per_departure")
    cols.append(seats * g("entry_month_load_factor"))  # entry-month passengers
    cols.append(seats)  # entry-month seats
    cols.append(seats * g("distance_miles"))  # entry-month available seat miles
    # gravity-model demand proxy: endpoint market sizes over squared distance (log scale)
    cols.append(np.log(np.maximum(g("origin_market_departures_prior_12m"), 1.0))
                + np.log(np.maximum(g("dest_market_departures_prior_12m"), 1.0))
                - 2.0 * np.log(np.maximum(g("distance_miles"), 1.0)))
    return np.column_stack(cols)
