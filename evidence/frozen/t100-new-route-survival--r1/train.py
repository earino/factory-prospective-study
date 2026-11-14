"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

# Shallow, strongly regularised trees: ~3.7k correlated rows (two directions per route, carrier-month cohorts).
# Each boosting round is a small bagged forest (num_parallel_tree) to cut seed variance.
PARAMS = {"n_estimators": 200, "max_depth": 2, "learning_rate": 0.03, "subsample": 0.5,
          "colsample_bynode": 0.5, "num_parallel_tree": 8, "min_child_weight": 5, "reg_lambda": 5.0}
RAW = ["distance_miles", "entry_calendar_month", "carrier_departures_prior_12m", "carrier_active_pairs_prior_12m",
       "carrier_route_attrition_prior_12m", "origin_market_departures_prior_12m", "dest_market_departures_prior_12m",
       "competing_carriers_prior_3m", "pair_departures_prior_3m", "entry_month_departures",
       "entry_month_seats_per_departure", "entry_month_load_factor", "carrier_new_at_origin", "carrier_new_at_dest"]
# Carrier-state columns and route columns enter additively (interaction constraint).
CAR = ["carrier_departures_prior_12m", "carrier_active_pairs_prior_12m", "carrier_route_attrition_prior_12m",
       "big_aircraft"]
# entry_month_departures and entry_month_load_factor are left out: entry_pax (departures x seats x load factor)
# already carries both.
ROUTE = ["entry_pax", "entry_calendar_month", "mkt_min", "mkt_ratio"]
COLS = CAR + ROUTE
# Domain prior: more carrier route churn -> more discontinuation; more entry-month volume -> less.
MONO = {"carrier_route_attrition_prior_12m": 1, "entry_pax": -1}
SENTINEL = -0.05   # real missing carrier values; NaN is reserved for the masked training copy
ROW_SHARE = 0.3    # share of total training weight given to the row-weighted, carrier-masked copy


def _features(X):
    # Row-local arithmetic on permitted predictors only; no state, no cross-row statistics.
    d = {c: X[c].to_numpy(dtype=float) for c in RAW}
    om, dm = d["origin_market_departures_prior_12m"], d["dest_market_departures_prior_12m"]
    with np.errstate(divide="ignore", invalid="ignore"):
        d["entry_pax"] = d["entry_month_departures"] * d["entry_month_seats_per_departure"] * d["entry_month_load_factor"]
        seats = d["entry_month_seats_per_departure"]
        # Coarse mainline/regional flag instead of exact seats, which fingerprints individual fleets.
        d["big_aircraft"] = np.where(np.isnan(seats), -1.0, (seats >= 100.0).astype(float))
        d["mkt_min"] = np.minimum(om, dm)
        d["mkt_ratio"] = np.minimum(om, dm) / np.maximum(om, dm)
    out = pd.DataFrame(d).replace([np.inf, -np.inf], np.nan)
    for c in CAR:
        out[c] = out[c].fillna(SENTINEL)
    return out


def fit(X_train, y_train, *, seed, threads):
    F = _features(X_train)[COLS]
    # Carrier-level predictors are constant within a carrier-month launch cohort; a few merger/recode cohorts
    # hold hundreds of rows. Group rows by that feature fingerprint (features only, no labels, no identifiers).
    key = X_train["carrier_departures_prior_12m"].astype(str) + "_" + X_train["carrier_active_pairs_prior_12m"].astype(str)
    n = key.map(key.value_counts()).to_numpy(dtype=float)
    # Copy A: all columns, equal total weight per cohort -> teaches the carrier part from cohorts.
    wa = 1.0 / n
    wa = wa / wa.sum() * (1.0 - ROW_SHARE)
    # Copy B: carrier columns masked, equal weight per row -> teaches the route part from every row.
    B = F.copy()
    B[CAR] = np.nan
    wb = np.full(len(F), ROW_SHARE / len(F))
    Z = pd.concat([F, B], ignore_index=True)
    yy = np.concatenate([np.asarray(y_train), np.asarray(y_train)])
    w = np.concatenate([wa, wb])
    w = w / w.mean()
    mono = "(" + ",".join(str(MONO.get(c, 0)) for c in COLS) + ")"
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, monotone_constraints=mono,
                          interaction_constraints=[CAR, ROUTE], **PARAMS)
    m.fit(Z, yy, sample_weight=w)
    return {"cols": COLS, "model": m}


def prepare(state, X):
    return _features(X)[state["cols"]]
