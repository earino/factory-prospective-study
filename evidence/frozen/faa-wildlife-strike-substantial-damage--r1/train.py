"""Self-contained XGBoost solution (configuration H5 = H4 + height-aware speed imputation; see REPORT.md).

One XGBClassifier on 44 features built from a single strike-report row plus fitted training state:
numeric/ordinal encodings, precipitation flags, one-hot categoricals (state unused), engines/mass ratio and
label-free imputation features for speed and height. Training-only devices: recency sample weights from the
order of the supplied training rows, and a 10% copy of training rows with reported size blanked.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

COLS = ["ac_mass", "ac_class", "num_engs", "type_eng", "phase_of_flt", "height_agl", "speed_kts",
        "distance_nm", "birds_struck", "birds_seen", "size", "warned", "time_of_day", "sky", "precip",
        "month", "state", "operator_class"]
BAND = {"1": 1.0, "2-10": 2.0, "11-100": 3.0, ">100": 4.0, "0": 0.0}
SIZE = {"SMALL": 1.0, "MEDIUM": 2.0, "LARGE": 3.0}
SKY = {"NO CLOUD": 0.0, "SOME CLOUD": 1.0, "OVERCAST": 2.0}
WARN = {"NO": 0.0, "YES": 1.0}
CATS = ["ac_class", "type_eng", "phase_of_flt", "time_of_day", "operator_class"]
NUMERIC = ["ac_mass", "num_engs", "height_agl", "speed_kts", "distance_nm", "month", "birds_struck",
           "birds_seen", "size", "warned", "sky", "p_fog", "p_rain", "p_snow", "p_any",
           "eng_per_mass", "speed_imp", "ke_imp", "speed_resid", "height_imp"]

MIN_COUNT = 50      # one-hot levels need this many training rows
RECENCY = 2.0       # sample weight = exp(RECENCY * (rank - 1)), rank in [0, 1] by training row order
SIZE_MASK = 0.1     # fraction of training rows duplicated with reported size blanked
PARAMS = {"n_estimators": 300, "max_depth": 6, "learning_rate": 0.03, "subsample": 0.8,
          "colsample_bytree": 0.7, "min_child_weight": 2, "reg_lambda": 10.0, "max_bin": 64}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def _hbin(h):
    """Height band used only as a key for speed imputation."""
    if h != h: return -1
    if h <= 0: return 0
    if h <= 200: return 1
    if h <= 1000: return 2
    if h <= 3000: return 3
    if h <= 8000: return 4
    return 5


def _isna(v):
    return v is None or (isinstance(v, float) and v != v)


def prepare(state, X):
    levels = state["levels"]
    imp = state["imp"]
    raw = X[COLS].to_numpy(dtype=object)
    nan = float("nan")
    out = np.empty((raw.shape[0], state["n_features"]), dtype=np.float32)
    for i in range(raw.shape[0]):
        (ac_mass, ac_class, num_engs, type_eng, phase, height, speed, dist, struck, seen, size, warned,
         tod, sky, precip, month, st, opc) = raw[i]
        ac_mass = _num(ac_mass); num_engs = _num(num_engs); height = _num(height)
        speed = _num(speed); dist = _num(dist); month = _num(month)
        b_struck = nan if _isna(struck) else BAND.get(str(struck), nan)
        b_seen = nan if _isna(seen) else BAND.get(str(seen), nan)
        sz = nan if _isna(size) else SIZE.get(str(size), nan)
        wn = nan if _isna(warned) else WARN.get(str(warned), nan)
        sk = nan if _isna(sky) else SKY.get(str(sky), nan)
        if _isna(precip):
            fog = rain = snow = pany = nan
        else:
            p = str(precip)
            fog = 1.0 if "FOG" in p else 0.0
            rain = 1.0 if "RAIN" in p else 0.0
            snow = 1.0 if "SNOW" in p else 0.0
            pany = 0.0 if p == "NONE" else 1.0
        # Label-free imputation: expected speed for this phase / mass / engine / height-band cell (falling back
        # to phase / mass / engine, then phase, then global), expected height by phase.
        ph = None if _isna(phase) else str(phase)
        te = None if _isna(type_eng) else str(type_eng)
        e_sp = imp["speed4"].get((ph, ac_mass, te, _hbin(height)))
        if e_sp is None:
            e_sp = imp["speed3"].get((ph, ac_mass, te))
        if e_sp is None:
            e_sp = imp["speed1"].get(ph, imp["speed0"])
        e_h = imp["height1"].get(ph, imp["height0"])
        sp_i = speed if speed == speed else e_sp
        row = [ac_mass, num_engs, height, speed, dist, month, b_struck, b_seen, sz, wn, sk, fog, rain, snow, pany,
               num_engs / ac_mass if ac_mass == ac_mass and ac_mass > 0 else nan,
               sp_i, sz * sp_i * sp_i / 1e4, speed - e_sp, height if height == height else e_h]
        vals = {"ac_class": ac_class, "type_eng": type_eng, "phase_of_flt": phase, "time_of_day": tod,
                "operator_class": opc}
        for c in CATS:
            v = vals[c]
            v = None if _isna(v) else str(v)
            row += [1.0 if v == lv else 0.0 for lv in levels[c]]
        out[i] = row
    return out


def fit(X_train, y_train, *, seed, threads):
    y = np.asarray(y_train)
    levels = {}
    for c in CATS:
        vc = X_train[c].dropna().astype(str).value_counts()
        levels[c] = sorted(vc[vc >= MIN_COUNT].index)
    # Imputation tables: training medians, no labels involved.
    d = X_train[["phase_of_flt", "ac_mass", "type_eng", "speed_kts", "height_agl"]]
    ds = d.dropna(subset=["speed_kts"])
    g3 = ds.groupby(["phase_of_flt", "ac_mass", "type_eng"]).speed_kts.agg(["median", "size"])
    g3 = g3[g3["size"] >= 20]["median"]
    d4 = ds.copy()
    d4["hb"] = [_hbin(float(h)) for h in d4.height_agl]
    g4 = d4.groupby(["phase_of_flt", "ac_mass", "type_eng", "hb"]).speed_kts.agg(["median", "size"])
    g4 = g4[g4["size"] >= 20]["median"]
    imp = {
        "speed4": {(str(k[0]), float(k[1]), str(k[2]), int(k[3])): float(v) for k, v in g4.items()},
        "speed3": {(str(k[0]), float(k[1]), str(k[2])): float(v) for k, v in g3.items()},
        "speed1": {str(k): float(v) for k, v in ds.groupby("phase_of_flt").speed_kts.median().items()},
        "speed0": float(ds.speed_kts.median()),
        "height1": {str(k): float(v) for k, v in
                    d.dropna(subset=["height_agl"]).groupby("phase_of_flt").height_agl.median().items()},
        "height0": float(d.height_agl.median()),
    }
    names = NUMERIC + [c + "=" + lv for c in CATS for lv in levels[c]]
    state = {"levels": levels, "imp": imp, "names": names, "n_features": len(names)}
    Z = prepare(state, X_train)
    # Recency weights from the order of the supplied training rows (the published file is chronological).
    rank = np.arange(len(y), dtype=float) / max(1, len(y) - 1)
    w = np.exp(RECENCY * (rank - 1.0))
    # Augmentation: copies of a random subset of training rows with reported size blanked.
    rs = np.random.RandomState(seed)
    idx = np.sort(rs.choice(len(y), int(SIZE_MASK * len(y)), replace=False))
    X2 = X_train.iloc[idx].copy()
    X2["size"] = np.nan
    Z = np.vstack([Z, prepare(state, X2)])
    w = np.concatenate([w, w[idx]])
    y = np.concatenate([y, y[idx]])
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, **PARAMS)
    m.fit(Z, y, sample_weight=w)
    state["model"] = m
    return state
