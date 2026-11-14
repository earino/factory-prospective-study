"""Self-contained XGBoost solution ."""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {'colsample_bytree': 0.4,
 'learning_rate': 0.03,
 'max_depth': 4,
 'min_child_weight': 5,
 'n_estimators': 150,
 'reg_lambda': 5.0,
 'subsample': 0.8}
KEEP = ['distance_miles', 'carrier_active_pairs_prior_12m', 'carrier_route_attrition_prior_12m',
 'competing_carriers_prior_3m', 'pair_departures_prior_3m', 'entry_month_seats_per_departure',
 'entry_month_load_factor', 'mkt_min', 'mkt_max', 'new_any', 'seats', 'pax', 'asm', 'rpm', 'entry_rel_freq']
DROP = []
MONO = {'asm': -1, 'carrier_route_attrition_prior_12m': 1, 'entry_rel_freq': -1, 'pax': -1, 'rpm': -1, 'seats': -1}
WEIGHT = None    # None | 'sqrt' | 'inv' | float power
SHRINK_K = 0     # shrink attrition toward training mean with k pseudo-pairs
INTER = None
DROP_UNIFORM = (8, 'pos')
def _features(X, st=None):
    out = X.copy()
    d = out["entry_month_departures"]; spd = out["entry_month_seats_per_departure"]; lf = out["entry_month_load_factor"]
    cd = out["carrier_departures_prior_12m"]; cp = out["carrier_active_pairs_prior_12m"]
    o = out["origin_market_departures_prior_12m"]; de = out["dest_market_departures_prior_12m"]
    pp = out["pair_departures_prior_3m"]; cc = out["competing_carriers_prior_3m"]; dist = out["distance_miles"]
    at = out["carrier_route_attrition_prior_12m"]
    out["seats"] = d * spd
    out["pax"] = d * spd * lf
    out["pax_per_dep"] = spd * lf
    out["empty_seats"] = d * spd * (1 - lf)
    out["carrier_deps_per_pair_month"] = cd / (12.0 * cp)
    out["entry_rel_freq"] = d / (cd / (12.0 * cp))
    out["mkt_min"] = np.minimum(o, de)
    out["mkt_max"] = np.maximum(o, de)
    out["mkt_ratio"] = np.minimum(o, de) / np.maximum(o, de)
    out["entry_share"] = d / (d + pp / 3.0)
    out["incumbent_deps_per_carrier"] = pp / (3.0 * cc.where(cc > 0))
    out["new_any"] = out["carrier_new_at_origin"] + out["carrier_new_at_dest"]
    out["carrier_share_small_mkt"] = cd / np.minimum(o, de)
    out["carrier_share_big_mkt"] = cd / np.maximum(o, de)
    out["route_share_small_mkt"] = d * 12.0 / np.minimum(o, de)
    out["asm"] = d * spd * dist
    out["rpm"] = d * spd * lf * dist
    out["attr_pairs"] = at * cp
    if st is not None and st.get("shrink_k", 0) > 0:
        k = st["shrink_k"]
        out["attr_shrunk"] = (at.fillna(st["attr_mean"]) * cp + st["attr_mean"] * k) / (cp + k)
    out["gauge_regional"] = ((spd > 30) & (spd <= 80)).astype(float)
    out["gauge_class"] = np.select([spd <= 19.5, spd <= 40, spd <= 56, spd <= 80, spd <= 130], [0.0, 1.0, 2.0, 3.0, 4.0], 5.0)
    out["gauge_frac"] = np.abs(spd - np.round(spd))
    out["regional_x_attr"] = out["gauge_regional"] * at
    out["pairs_per_gauge"] = cp / spd
    m = out["entry_calendar_month"]
    out["month_cos"] = np.cos(2 * np.pi * m / 12.0)
    out["month_sin"] = np.sin(2 * np.pi * m / 12.0)
    return out

def fit(X_train, y_train, *, seed, threads):
    state = {"shrink_k": SHRINK_K, "attr_mean": float(X_train["carrier_route_attrition_prior_12m"].mean())}
    F = _features(X_train, state)
    cols = list(KEEP) if KEEP is not None else [c for c in F.columns if c not in DROP]
    state["cols"] = cols
    w = None
    if WEIGHT is not None:
        key = X_train["carrier_departures_prior_12m"].astype(str) + "_" + X_train["carrier_active_pairs_prior_12m"].astype(str)
        n = key.map(key.value_counts()).to_numpy().astype(float)
        if isinstance(WEIGHT, (tuple, list)):   # ('cap', c): a carrier-month cohort carries at most c rows of weight
            w = np.minimum(1.0, WEIGHT[1] / n)
        else:
            pw = {"sqrt": 0.5, "inv": 1.0}.get(WEIGHT, WEIGHT)
            w = n ** (-pw)
        w = w / w.mean()
    keep_rows = np.ones(len(X_train), dtype=bool)
    if DROP_UNIFORM is not None:
        ck = (X_train["carrier_departures_prior_12m"].astype(str) + "_" + X_train["carrier_active_pairs_prior_12m"].astype(str)).to_numpy()
        ys = pd.Series(np.asarray(y_train, dtype=float))
        cn = ys.groupby(ck).transform("size").to_numpy(); cr = ys.groupby(ck).transform("mean").to_numpy()
        thr = DROP_UNIFORM[2] if len(DROP_UNIFORM) > 2 else 1.0
        uni = (cr >= thr) if DROP_UNIFORM[1] == "pos" else ((cr >= thr) | (cr <= 1.0 - thr))
        keep_rows = ~((cn >= DROP_UNIFORM[0]) & uni)
    state["rows_dropped"] = int((~keep_rows).sum())
    mono = None
    if MONO:
        mono = "(" + ",".join(str(MONO.get(c, 0)) for c in cols) + ")"
    inter = None
    if INTER:
        inter = [[c for c in g if c in cols] for g in INTER]
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, monotone_constraints=mono,
                          interaction_constraints=inter, **PARAMS)
    m.fit(prepare(state, X_train)[keep_rows], np.asarray(y_train)[keep_rows], sample_weight=None if w is None else w[keep_rows])
    state["model"] = m
    return state

def prepare(state, X):
    return _features(X, state)[state["cols"]].astype(float)
