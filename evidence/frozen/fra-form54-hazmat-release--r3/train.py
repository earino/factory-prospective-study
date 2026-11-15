"""Self-contained XGBoost solution (clean rewrite of the selected H12 configuration).

One depth-2 XGBClassifier on 19 features built from 8 of the 14 released inputs:
speed, tonnage, row-local ratio / speed-weighted consist features, track type (frequency rank),
and out-of-fold target means for accident type and state (state shrunk toward a distance-kernel
average of the surrounding states).
Training uses a time-local base-rate logit offset computed from training row order (the supplied
training frame is chronological); scoring needs no time input, no row order and no batch statistics.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {"n_estimators": 200, "max_depth": 2, "learning_rate": 0.03, "subsample": 1.0,
          "colsample_bytree": 1.0, "min_child_weight": 5, "reg_lambda": 5.0}
TE_SMOOTH = 400.0      # pseudo-count pulling an accident type's target mean toward the global prior
STATE_SMOOTH = 2000.0  # pseudo-count pulling a state's target mean toward its spatial-neighbourhood mean
PARENT_SMOOTH = 50.0   # pseudo-count pulling the neighbourhood mean toward the global prior
KERNEL_KM = 750.0      # Gaussian kernel bandwidth over state centroids
TE_FOLDS = 5
WINDOW = 500           # half-width (rows) of the time-local base-rate window
MISSING = "__NA__"
NUMERIC = ["trainspeed", "grosstonnage", "haz_frac", "haz_per_loaded", "loaded_frac", "tons_per_car",
           "energy", "speed_x_haz", "speed_x_cars", "hazfrac_sp2", "loaded_x_sp", "gt_zero",
           "tons_x_hazfrac", "p_any_a", "p_any_b", "p_any_c"]
NAMES = NUMERIC + ["tracktype", "accidenttype", "stateabbr"]

# Approximate state centroids (latitude, longitude west-positive); static geography, no labels.
LATLON = {"AL": (32.8, 86.8), "AK": (64.0, 152.0), "AZ": (34.2, 111.7), "AR": (34.9, 92.4), "CA": (37.2, 119.4),
          "CO": (39.0, 105.5), "CT": (41.6, 72.7), "DE": (39.0, 75.5), "DC": (38.9, 77.0), "FL": (28.6, 82.4),
          "GA": (32.7, 83.4), "HI": (20.3, 156.4), "ID": (44.4, 114.6), "IL": (40.0, 89.2), "IN": (39.9, 86.3),
          "IA": (42.1, 93.5), "KS": (38.5, 98.4), "KY": (37.5, 85.3), "LA": (31.1, 92.0), "ME": (45.4, 69.2),
          "MD": (39.0, 76.8), "MA": (42.3, 71.8), "MI": (44.3, 85.4), "MN": (46.3, 94.3), "MS": (32.7, 89.7),
          "MO": (38.4, 92.5), "MT": (47.0, 109.6), "NE": (41.5, 99.8), "NV": (39.3, 116.6), "NH": (43.7, 71.6),
          "NJ": (40.2, 74.7), "NM": (34.4, 106.1), "NY": (42.9, 75.5), "NC": (35.6, 79.4), "ND": (47.5, 100.5),
          "OH": (40.3, 82.8), "OK": (35.6, 97.5), "OR": (43.9, 120.6), "PA": (40.9, 77.8), "RI": (41.7, 71.6),
          "SC": (33.9, 80.9), "SD": (44.4, 100.2), "TN": (35.9, 86.4), "TX": (31.5, 99.3), "UT": (39.3, 111.7),
          "VT": (44.1, 72.7), "VA": (37.5, 78.8), "WA": (47.4, 120.5), "WV": (38.6, 80.6), "WI": (44.6, 89.9),
          "WY": (43.0, 107.5)}


def _num(X, c):
    return pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float)


def _cat(X, c):
    v = X[c].to_numpy(dtype=object)
    return np.array([MISSING if (x is None or x != x) else str(x).strip() for x in v], dtype=object)


def _numeric(X):
    """Row-local features; no fitted state and no cross-row computation."""
    sp = _num(X, "trainspeed"); hz = _num(X, "hazmatcars"); ld = _num(X, "loadedfreightcars")
    em = _num(X, "emptyfreightcars"); gt = _num(X, "grosstonnage")
    f = {}
    f["trainspeed"] = sp
    f["grosstonnage"] = gt
    tot = ld + em
    f["haz_frac"] = hz / np.maximum(tot, 1.0)
    f["haz_per_loaded"] = hz / np.maximum(ld, 1.0)
    f["loaded_frac"] = ld / np.maximum(tot, 1.0)
    f["tons_per_car"] = gt / np.maximum(tot, 1.0)
    f["energy"] = gt * sp * sp
    f["speed_x_haz"] = sp * hz
    f["speed_x_cars"] = sp * tot
    f["hazfrac_sp2"] = f["haz_frac"] * sp * sp
    f["loaded_x_sp"] = ld * sp
    f["gt_zero"] = (gt == 0).astype(float)       # zero tonnage is a not-recorded code
    f["tons_x_hazfrac"] = gt * f["haz_frac"]
    # Chance that at least one hazmat car is among the derailed cars, if the number of derailed
    # cars grows with speed (constants chosen a priori, not fitted).
    hf = np.minimum(f["haz_frac"], 1.0)
    f["p_any_a"] = 1.0 - (1.0 - hf) ** (1.0 + 0.2 * sp)
    f["p_any_b"] = 1.0 - (1.0 - hf) ** (1.0 + 0.5 * sp)
    f["p_any_c"] = 1.0 - (1.0 - hf) ** (1.0 + 0.02 * sp * sp)
    return f


def _te_map(keys, y, prior, smooth):
    df = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    return {k: (s + prior * smooth) / (n + smooth) for k, s, n in zip(df.index, df["sum"], df["count"])}


def _te_geo(keys, y, prior, smooth, smooth_parent, bw):
    """State mean shrunk toward a distance-kernel average of all states' rates (spatial smoothing)."""
    df = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    ks = list(df.index); S = df["sum"].to_numpy(dtype=float); N = df["count"].to_numpy(dtype=float)
    ll = np.array([LATLON.get(k, (np.nan, np.nan)) for k in ks], dtype=float)
    out = {}
    for i, k in enumerate(ks):
        if np.isnan(ll[i, 0]):
            par = prior
        else:
            dlat = (ll[:, 0] - ll[i, 0]) * 111.0
            dlon = (ll[:, 1] - ll[i, 1]) * 111.0 * np.cos(np.radians(ll[i, 0]))
            w = np.exp(-(dlat ** 2 + dlon ** 2) / (bw * bw)); w[np.isnan(w)] = 0.0
            par = (float((w * S).sum()) + prior * smooth_parent) / (float((w * N).sum()) + smooth_parent)
        out[k] = (S[i] + par * smooth) / (N[i] + smooth)
    return out


def _encode(c, keys, y, prior):
    if c == "stateabbr":
        return _te_geo(keys, y, prior, STATE_SMOOTH, PARENT_SMOOTH, KERNEL_KM)
    return _te_map(keys, y, prior, TE_SMOOTH)


def fit(X_train, y_train, *, seed, threads):
    y = np.asarray(y_train).astype(int)
    n = len(y)
    yt = y.astype(float)
    prior = float(y.mean())
    cols = _numeric(X_train)
    state = {"maps": {}, "default": {}}

    # Track type: frequency-rank ordinal (unseen -> missing).
    k = _cat(X_train, "tracktype")
    vc = pd.Series(k).value_counts()
    state["maps"]["tracktype"] = {v: float(i) for i, v in enumerate(vc.index)}
    state["default"]["tracktype"] = np.nan
    cols["tracktype"] = np.array([state["maps"]["tracktype"].get(v, np.nan) for v in k], dtype=float)

    # Accident type and state: smoothed target means. Scoring rows use the full-training map;
    # training rows get out-of-fold values, so a row's own label never enters its encoding
    # (neither the level mean, nor the neighbourhood mean, nor the prior).
    for c in ("accidenttype", "stateabbr"):
        k = _cat(X_train, c)
        state["maps"][c] = _encode(c, k, yt, prior)
        state["default"][c] = prior
        fold = np.random.RandomState(seed + 17).randint(0, TE_FOLDS, size=n)
        oof = np.zeros(n, dtype=float)
        for j in range(TE_FOLDS):
            tr_i = fold != j; te_i = ~tr_i
            pj = float(yt[tr_i].mean())
            mj = _encode(c, k[tr_i], yt[tr_i], pj)
            oof[te_i] += np.array([mj.get(v, pj) for v in k[te_i]])
        cols[c] = oof

    M = np.column_stack([cols[f] for f in NAMES]).astype(np.float32)

    # Time-local base rate. Training rows arrive in chronological order and the release rate falls
    # strongly over the training era, so a centred moving-window rate over neighbouring training rows
    # (own label excluded from the window and from its smoothing prior) enters as a fixed logit offset; trees then learn within-era effects instead
    # of using drifting covariates as an era proxy. Scoring rows get the constant base_score (rate of
    # the latest training window).
    cs = np.concatenate([[0.0], np.cumsum(y)])
    idx = np.arange(n)
    lo = np.maximum(idx - WINDOW, 0); hi = np.minimum(idx + WINDOW + 1, n)
    prior_loo = (float(y.sum()) - y) / max(n - 1, 1)     # global rate without the row's own label
    r_local = ((cs[hi] - cs[lo] - y) + prior_loo * 20.0) / ((hi - lo - 1).astype(float) + 20.0)
    offset = np.log(r_local / (1.0 - r_local))
    last = float(y[max(n - 2 * WINDOW, 0):].mean())

    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads,
                          base_score=min(max(last, 1e-3), 0.5), **PARAMS)
    m.fit(M, y, base_margin=offset)
    state["model"] = m
    return state


def prepare(state, X):
    cols = _numeric(X)
    for c in ("tracktype", "accidenttype", "stateabbr"):
        mp = state["maps"][c]; d = state["default"][c]
        cols[c] = np.array([mp.get(v, d) for v in _cat(X, c)], dtype=float)
    return np.column_stack([cols[f] for f in NAMES]).astype(np.float32)
