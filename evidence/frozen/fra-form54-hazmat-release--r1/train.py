"""Self-contained XGBoost solution for fra-form54-hazmat-release.

One shallow, regularised XGBClassifier on row-wise features, with a restricted interaction structure.

fit() learns only the category levels seen in the fitting rows and the trees.
prepare() is strictly row-wise: every output value depends on that one row plus fitted state.
No date, identifier, target statistic, file or batch statistic is used.

Left out on purpose (see REPORT.md): weather, visibility, temperature and reporting railroad class carry no
signal in any era; tons per car is confounded with calendar era in the training period; the raw empty-car count
is used only through total cars and shares.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

RAW_NUM = ["trainspeed", "hazmatcars", "loadedfreightcars", "emptyfreightcars", "grosstonnage"]
ONEHOT = ["equipmenttype", "tracktype", "accidenttype", "stateabbr"]
PARAMS = dict(n_estimators=500, max_depth=2, learning_rate=0.03, subsample=0.9, colsample_bytree=0.7,
              min_child_weight=10)
# Interaction structure. Every feature may interact with the accident-type and track-type dummies (the context
# of the event). Numeric features may not interact with each other, except a small physical core:
# speed, hazmat share, loaded share and speed x hazmat share.
CONTEXT = ("accidenttype=", "tracktype=")
CORE = ["trainspeed", "sp_hzfrac", "hz_frac", "ld_frac"]
# FRA maximum freight speed by track class (49 CFR 213.9); excepted track ("X", coded -1) is 10 mph.
SPEED_LIMIT = {-1.0: 10.0, 1.0: 10.0, 2.0: 25.0, 3.0: 40.0, 4.0: 60.0, 5.0: 80.0, 6.0: 110.0}
# Loaded share of the consist may only raise predicted release risk (loaded cars carry product).
MONOTONE = {"ld_frac": 1}


def _num(X, col):
    return pd.to_numeric(X[col], errors="coerce").to_numpy(dtype=float)


def _trackclass(v):
    # FRA track class 1-9 as a number; excepted track "X" as -1; anything else missing.
    if v is None or v != v:
        return np.nan
    if str(v).strip().upper() == "X":
        return -1.0
    try:
        return float(v)
    except Exception:
        return np.nan


def fit(X_train, y_train, *, seed, threads):
    y_train = np.asarray(y_train)
    levels = {c: sorted(X_train[c].dropna().unique()) for c in ONEHOT}
    state = {"levels": levels}
    Z = prepare(state, X_train)
    ctx = [c for c in Z.columns if c.startswith(CONTEXT)]
    groups = [[c] + ctx for c in Z.columns if c not in ctx] + [CORE + ctx]
    model = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, random_state=seed, n_jobs=threads,
                              monotone_constraints=dict(MONOTONE), interaction_constraints=groups, **PARAMS)
    model.fit(Z, y_train)
    state["model"] = model
    return state


def prepare(state, X):
    sp = _num(X, "trainspeed")
    hz = _num(X, "hazmatcars")
    ld = _num(X, "loadedfreightcars")
    em = _num(X, "emptyfreightcars")
    tn = _num(X, "grosstonnage")
    # The raw empty-car count is not passed on its own; it enters through total cars and the shares below.
    out = {"trainspeed": sp, "hazmatcars": hz, "loadedfreightcars": ld, "grosstonnage": tn}
    tc = np.array([_trackclass(v) for v in X["trackclass"].astype(object).to_numpy()])
    out["trackclass"] = tc

    cars = ld + em
    c1 = np.maximum(cars, 1.0)
    tpos = np.where(tn > 0, tn, np.nan)            # zero tonnage means "not reported" (yard moves)
    hzf = np.where(cars > 0, hz / c1, np.nan)
    out["cars"] = cars                              # consist length
    out["hz_frac"] = hzf                            # hazmat share of the consist
    out["hz_ld_frac"] = np.where(ld > 0, hz / np.maximum(ld, 1.0), np.nan)
    out["ld_frac"] = np.where(cars > 0, ld / c1, np.nan)
    out["ton0"] = (tn == 0).astype(float)
    out["ke"] = np.log1p(tpos * sp * sp)            # kinetic energy
    out["mom"] = np.log1p(tpos * sp)                # momentum
    out["sp_hz"] = sp * hz
    out["sp2_cars"] = np.log1p(sp * sp * cars)
    out["sp_hzfrac"] = sp * hzf
    out["hz_gt_ld"] = (hz > ld).astype(float)
    out["hz_minus_ld"] = hz - ld
    out["exp_hz"] = np.log1p(sp) * np.log1p(hz)
    out["sp_lim"] = sp / np.array([SPEED_LIMIT.get(v, np.nan) for v in tc])   # speed relative to the class limit
    out = pd.DataFrame(out, index=X.index)

    for c in ONEHOT:
        xc = X[c].to_numpy()
        for k in state["levels"][c]:
            out[c + "=" + str(k)] = (xc == k).astype(float)   # unseen or missing level -> all zeros
    return out
