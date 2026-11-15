"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.03,
    "subsample": 0.8,
    "colsample_bytree": 0.7,
    "min_child_weight": 3,
    "reg_lambda": 5.0,
    "gamma": 0.0,
    "max_bin": 256,
    "max_cat_to_onehot": 1,  # native categoricals always use partition (grouping) splits
}
CFG = {
    "state": "drop",          # "te" (out-of-fold smoothed target rate), "drop"
    "te_smooth": 50.0,
    "te_folds": 5,
    "onehot": True,         # one-hot the small nominal fields
    "missing": False,        # report-completeness counts
    "inter": False,          # hand-built interactions
    "cyc": False,            # cyclical month
    "recency": 2.0,         # >0: weight rises with training row position (see REPORT)
    "monotone": False,
    "phase_min": 200,         # collapse flight phases with fewer training rows than this to missing
    "latlon": True,        # approximate state centroid (fixed geographic constants)
    "st_season": False,     # OOF target rate of state x season
    "drop": ["ph_"],             # feature-name prefixes removed from the matrix
    "drop_exact": [],
    "tod_onehot": False,
    "native_combos": [],    # "+"-joined raw columns; combinations with >=100 training rows become one native categorical
    "native": ["phase", "mass", "aircraft"],           # fields also passed as native XGBoost categoricals: phase, eng, op, state
    "geo_rot": False,
    "geo_season": False,
    "te_keys": [],          # extra OOF target-rate encodings, each a "+"-joined list of raw columns
    "additive": [],         # feature-name prefixes barred from interacting with other features
    "mask_aug": {},         # {"cols": [...], "frac": f, "w": weight}: extra training copies with fields blanked
    "impute": True,        # speed/height filled from training medians by (phase, mass)
}
LATLON = {"AK": (64.0, -152.0), "AL": (32.8, -86.8), "AR": (34.9, -92.4), "AZ": (34.2, -111.7),
          "CA": (37.2, -119.4), "CO": (39.0, -105.5), "CT": (41.6, -72.7), "DC": (38.9, -77.0),
          "DE": (39.0, -75.5), "FL": (28.6, -82.4), "GA": (32.7, -83.4), "HI": (20.8, -156.3),
          "IA": (42.1, -93.5), "ID": (44.4, -114.6), "IL": (40.0, -89.2), "IN": (39.9, -86.3),
          "KS": (38.5, -98.4), "KY": (37.5, -85.3), "LA": (31.1, -92.0), "MA": (42.3, -71.8),
          "MD": (39.0, -76.8), "ME": (45.4, -69.2), "MI": (44.3, -85.4), "MN": (46.3, -94.3),
          "MO": (38.4, -92.5), "MS": (32.7, -89.7), "MT": (47.0, -109.6), "NC": (35.6, -79.4),
          "ND": (47.5, -100.5), "NE": (41.5, -99.8), "NH": (43.7, -71.6), "NJ": (40.2, -74.7),
          "NM": (34.4, -106.1), "NV": (39.3, -116.6), "NY": (42.9, -75.5), "OH": (40.3, -82.8),
          "OK": (35.6, -97.5), "OR": (43.9, -120.6), "PA": (40.9, -77.8), "RI": (41.7, -71.5),
          "SC": (33.9, -80.9), "SD": (44.4, -100.2), "TN": (35.9, -86.4), "TX": (31.5, -99.3),
          "UT": (39.3, -111.7), "VA": (37.5, -78.9), "VT": (44.1, -72.7), "WA": (47.4, -120.5),
          "WI": (44.6, -89.9), "WV": (38.6, -80.6), "WY": (43.0, -107.5)}
SEASON = {12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 0}

SIZE = {"SMALL": 0.0, "MEDIUM": 1.0, "LARGE": 2.0}
BAND = {"0": 0.0, "1": 1.0, "2-10": 2.0, "11-100": 3.0, ">100": 4.0}
WARN = {"NO": 0.0, "YES": 1.0}
SKY = {"NO CLOUD": 0.0, "SOME CLOUD": 1.0, "OVERCAST": 2.0}
TOD = {"DAY": 0.0, "DAWN": 1.0, "DUSK": 2.0, "NIGHT": 3.0}
PHASES = ["APPROACH", "ARRIVAL", "CLIMB", "DEPARTURE", "DESCENT", "LANDING ROLL",
          "LOCAL", "PARKED", "TAKE-OFF RUN", "TAXI"]
# coarse ordering of flight phases along a ground -> airborne axis
PHASE_ORD = {"PARKED": 0.0, "TAXI": 1.0, "LANDING ROLL": 2.0, "TAKE-OFF RUN": 3.0,
             "ARRIVAL": 4.0, "APPROACH": 4.0, "LOCAL": 5.0, "DEPARTURE": 6.0,
             "CLIMB": 6.0, "DESCENT": 7.0, "EN ROUTE": 8.0}
ENG = ["A", "B", "C", "D", "F"]
OPS = ["airline", "BUS", "PVT", "GOV"]
RAW_ALL = ["ac_mass", "ac_class", "num_engs", "type_eng", "phase_of_flt", "height_agl",
           "speed_kts", "distance_nm", "birds_struck", "birds_seen", "size", "warned",
           "time_of_day", "sky", "precip", "operator_class"]
PILOT = ["height_agl", "speed_kts", "distance_nm", "birds_seen", "warned", "time_of_day",
         "sky", "precip", "size"]


def _num(X, c):
    return pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float)


def _tok(v):
    # strings pass through; a band such as "1" that a CSV reader parsed as a number is restored
    if isinstance(v, str):
        return v
    if v is None or v != v:
        return None
    try:
        return str(int(v)) if float(v).is_integer() else str(v)
    except (TypeError, ValueError):
        return None


def _str(X, c):
    return [_tok(v) for v in X[c].tolist()]


def _map(vals, d):
    return np.array([d.get(v, np.nan) if v is not None else np.nan for v in vals], dtype=float)


def _features(cfg, X):
    """Row-independent features. Returns (names, float32 matrix)."""
    f = {}
    n = len(X)
    mass = _num(X, "ac_mass"); engs = _num(X, "num_engs")
    h = _num(X, "height_agl"); s = _num(X, "speed_kts"); d = _num(X, "distance_nm")
    month = _num(X, "month")
    size = _map(_str(X, "size"), SIZE)
    struck = _map(_str(X, "birds_struck"), BAND)
    seen = _map(_str(X, "birds_seen"), BAND)
    phase = _str(X, "phase_of_flt")
    if cfg.get("phase_keep") is not None:
        phase = [v if v in cfg["phase_keep"] else None for v in phase]
    eng = _str(X, "type_eng")
    op = _str(X, "operator_class"); acc = _str(X, "ac_class")
    precip = _str(X, "precip")
    f["ac_mass"] = mass; f["num_engs"] = engs; f["height_agl"] = h; f["speed_kts"] = s
    f["distance_nm"] = d; f["month"] = month; f["size"] = size
    f["birds_struck"] = struck; f["birds_seen"] = seen
    f["warned"] = _map(_str(X, "warned"), WARN)
    f["sky"] = _map(_str(X, "sky"), SKY)
    f["time_of_day"] = _map(_str(X, "time_of_day"), TOD)
    f["phase_ord"] = _map(phase, PHASE_ORD)
    f["ac_class_A"] = np.array([np.nan if v is None else float(v == "A") for v in acc])
    f["precip_none"] = np.array([np.nan if v is None else float(v == "NONE") for v in precip])
    f["precip_fog"] = np.array([np.nan if v is None else float("FOG" in v) for v in precip])
    f["precip_rain"] = np.array([np.nan if v is None else float("RAIN" in v) for v in precip])
    f["precip_snow"] = np.array([np.nan if v is None else float("SNOW" in v) for v in precip])
    if cfg["onehot"]:
        for p in PHASES:
            f["ph_" + p] = np.array([float(v == p) for v in phase])
        for e in ENG:
            f["eng_" + e] = np.array([float(v == e) for v in eng])
        for o in OPS:
            f["op_" + o] = np.array([float(v == o) for v in op])
    else:
        f["eng_code"] = _map(eng, {e: float(i) for i, e in enumerate(ENG)})
        f["op_code"] = _map(op, {o: float(i) for i, o in enumerate(OPS)})
    nat = cfg.get("native") or []
    if "phase" in nat:
        f["nat_phase"] = _map(phase, {p: float(i) for i, p in enumerate(PHASES)})
    if "eng" in nat:
        f["nat_eng"] = _map(eng, {e: float(i) for i, e in enumerate(ENG)})
    if "op" in nat:
        f["nat_op"] = _map(op, {o: float(i) for i, o in enumerate(OPS)})
    if "state" in nat:
        f["nat_state"] = _map(_str(X, "state"), {k: float(i) for i, k in enumerate(sorted(LATLON))})
    if "phase_size" in nat:
        pc = _map(phase, {p: float(i) for i, p in enumerate(PHASES)})
        f["nat_phase_size"] = np.where(np.isfinite(pc), pc * 4.0 + np.where(np.isfinite(size), size, 3.0), np.nan)
    if "mass" in nat:
        f["nat_mass"] = np.where((mass >= 1) & (mass <= 5), mass - 1.0, np.nan)
    if "engs" in nat:
        f["nat_engs"] = np.where((engs >= 1) & (engs <= 4), engs - 1.0, np.nan)
    if "size" in nat:        # missing size is its own category
        f["nat_size"] = np.where(np.isfinite(size), size, 3.0)
    if "struck" in nat:      # missing band is its own category
        f["nat_struck"] = np.where(np.isfinite(struck), struck, 5.0)
    if "month" in nat:
        f["nat_month"] = np.where((month >= 1) & (month <= 12), month - 1.0, np.nan)
    if "tod" in nat:
        f["nat_tod"] = _map(_str(X, "time_of_day"), TOD)
    if "aircraft" in nat:
        key = [None if not (np.isfinite(a) and np.isfinite(b)) or c is None else "%d|%d|%s" % (a, b, c)
               for a, b, c in zip(mass, engs, eng)]
        f["nat_aircraft"] = _map(key, cfg.get("ac_vocab") or {})
    for combo in cfg.get("native_combos") or []:
        f["nat_c_" + combo] = _map(_keys(X, combo), (cfg.get("combo_vocab") or {}).get(combo, {}))
    if cfg.get("tod_onehot"):
        tod = _str(X, "time_of_day")
        for t in TOD:
            f["tod_" + t] = np.array([np.nan if v is None else float(v == t) for v in tod])
    if cfg["missing"]:
        isna = X[RAW_ALL].isna().to_numpy()
        f["n_missing"] = isna.sum(axis=1).astype(float)
        f["n_missing_pilot"] = X[PILOT].isna().to_numpy().sum(axis=1).astype(float)
    if cfg["cyc"]:
        f["month_sin"] = np.sin(2 * np.pi * month / 12.0)
        f["month_cos"] = np.cos(2 * np.pi * month / 12.0)
    if cfg["inter"]:
        f["energy"] = (size + 1.0) * s * s          # crude kinetic-energy proxy
        f["size_x_struck"] = (size + 1.0) * struck
        f["size_x_mass"] = size * 10.0 + mass
        f["mass_x_engs"] = mass * 10.0 + engs
        f["struck_minus_seen"] = struck - seen
        f["speed_per_mass"] = s / mass
        f["h_per_d"] = h / (d + 0.5)
        f["size_x_op"] = size * 10.0 + _map(op, {o: float(i) for i, o in enumerate(OPS)})
    if cfg.get("imp_tab") is not None:
        tab = cfg["imp_tab"]
        ph0 = _str(X, "phase_of_flt")
        for nm, raw in (("speed_kts", s), ("height_agl", h)):
            t = tab[nm]
            fill = np.array([t.get((p, m), t.get((p, None), t[None])) for p, m in
                             zip(ph0, [None if not np.isfinite(v) else float(v) for v in mass])])
            f[nm + "_imp"] = np.where(np.isfinite(raw), raw, fill)
        f["energy_imp"] = (np.where(np.isfinite(size), size, 0.5) + 1.0) * f["speed_kts_imp"] ** 2
    if cfg["latlon"]:
        st = _str(X, "state")
        f["lat"] = np.array([LATLON.get(v, (np.nan, np.nan))[0] for v in st])
        f["lon"] = np.array([LATLON.get(v, (np.nan, np.nan))[1] for v in st])
        if cfg.get("geo_rot"):
            f["geo_ne"] = f["lat"] + f["lon"] * 0.5
            f["geo_nw"] = f["lat"] - f["lon"] * 0.5
        if cfg.get("geo_season"):
            # seasonal cold proxy: latitude scaled by distance of the month from midsummer
            mth = _num(X, "month")
            f["cold"] = (f["lat"] - 25.0) * (1.0 + np.cos(2 * np.pi * (mth - 1.0) / 12.0))
    names = [k for k in f if not any(k.startswith(p) for p in cfg["drop"]) and k not in cfg["drop_exact"]]
    M = np.empty((n, len(names)), dtype=np.float32)
    for j, k in enumerate(names):
        M[:, j] = f[k]
    M[~np.isfinite(M)] = np.nan
    return names, M


def _te_lookup(te, vals):
    return np.array([te["map"].get(v, te["prior"]) for v in vals], dtype=np.float32)


def _te_fit(vals, y, smooth):
    prior = float(y.mean())
    df = pd.DataFrame({"k": vals, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    rate = (df["sum"] + smooth * prior) / (df["count"] + smooth)
    return {"map": rate.to_dict(), "prior": prior}


def _keys(X, which):
    st = _str(X, "state")
    if which == "state":
        return st
    if which == "st_season":
        mo = _num(X, "month")
        return [None if a is None or not np.isfinite(b) else a + "|" + str(SEASON.get(int(b), -1))
                for a, b in zip(st, mo)]
    cols = [_str(X, c) for c in which.split("+")]
    return ["|".join("?" if v is None else v for v in t) for t in zip(*cols)]


def prepare(state, X):
    names, M = _features(state["cfg"], X)
    cols = [M] + [_te_lookup(te, _keys(X, which)) for which, te in state["te"]]
    return np.column_stack(cols).astype(np.float32) if len(cols) > 1 else M


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    y = np.asarray(y_train).astype(int)
    X_train = X_train.reset_index(drop=True)
    if cfg["phase_min"] > 0:
        vc = X_train["phase_of_flt"].value_counts()
        cfg["phase_keep"] = set(vc[vc >= cfg["phase_min"]].index)
    if cfg["impute"]:
        tab = {}
        g = pd.DataFrame({"p": _str(X_train, "phase_of_flt"), "m": _num(X_train, "ac_mass"),
                          "speed_kts": _num(X_train, "speed_kts"), "height_agl": _num(X_train, "height_agl")})
        for nm in ("speed_kts", "height_agl"):
            t = {None: float(g[nm].median())}
            for p, v in g.groupby("p")[nm].median().dropna().items():
                t[(p, None)] = float(v)
            for (p, m), v in g.groupby(["p", "m"])[nm].median().dropna().items():
                t[(p, float(m))] = float(v)
            tab[nm] = t
        cfg["imp_tab"] = tab
    if "aircraft" in (cfg.get("native") or []):
        g = pd.DataFrame({"a": _num(X_train, "ac_mass"), "b": _num(X_train, "num_engs"),
                          "c": _str(X_train, "type_eng")}).dropna()
        keys = (g["a"].astype(int).astype(str) + "|" + g["b"].astype(int).astype(str) + "|" + g["c"]).value_counts()
        cfg["ac_vocab"] = {k: float(i) for i, k in enumerate(sorted(keys[keys >= cfg.get("ac_min", 100)].index))}
    cfg["combo_vocab"] = {}
    for combo in cfg.get("native_combos") or []:
        vc = pd.Series(_keys(X_train, combo)).value_counts()
        cfg["combo_vocab"][combo] = {k: float(i) for i, k in enumerate(sorted(vc[vc >= 100].index))}
    state = {"cfg": cfg, "te": []}
    names, M = _features(cfg, X_train)
    whichs = (["state"] if cfg["state"] == "te" else []) + (["st_season"] if cfg["st_season"] else []) + list(cfg["te_keys"])
    if whichs:
        # out-of-fold encoding: a row's own label never enters its rate or its prior
        rng = np.random.RandomState(seed)
        fold = rng.randint(0, cfg["te_folds"], size=len(y))
        extra = []
        for which in whichs:
            keys = np.array(_keys(X_train, which), dtype=object)
            col = np.empty(len(y), dtype=np.float32)
            for k in range(cfg["te_folds"]):
                tr = fold != k
                col[~tr] = _te_lookup(_te_fit(keys[tr], y[tr], cfg["te_smooth"]), keys[~tr])
            extra.append(col); names = names + [which + "_te"]
            state["te"].append((which, _te_fit(keys, y, cfg["te_smooth"])))
        M = np.column_stack([M] + extra).astype(np.float32)
    w = None
    if cfg["recency"] > 0:
        pos = np.arange(len(y)) / max(1, len(y) - 1)
        w = np.exp(cfg["recency"] * (pos - 1.0))
    aug = cfg.get("mask_aug") or {}
    if aug:
        rng2 = np.random.RandomState(seed + 1)
        idx = np.flatnonzero(rng2.rand(len(y)) < aug["frac"])
        Xa = X_train.iloc[idx].copy()
        for c in aug["cols"]:
            Xa[c] = np.nan
        _, Ma = _features(cfg, Xa)
        extra = [_te_lookup(te, _keys(Xa, which)) for which, te in state["te"]]
        if extra:
            Ma = np.column_stack([Ma] + extra).astype(np.float32)
        base_w = np.ones(len(y)) if w is None else w
        M = np.vstack([M, Ma]); w = np.concatenate([base_w, base_w[idx] * aug["w"]])
        y = np.concatenate([y, y[idx]])
    kw = {}
    if cfg["monotone"]:
        inc = {"size", "birds_struck", "energy", "size_x_struck"}
        kw["monotone_constraints"] = "(" + ",".join("1" if k in inc else "0" for k in names) + ")"
    if cfg["additive"]:
        weak = [j for j, k in enumerate(names) if any(k.startswith(p) for p in cfg["additive"])]
        core = [j for j in range(len(names)) if j not in weak]
        kw["interaction_constraints"] = str([core] + [[j] for j in weak])
    if cfg.get("native"):
        kw["feature_types"] = ["c" if k.startswith("nat_") else "q" for k in names]
        kw["enable_categorical"] = True
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads,
                          eval_metric="auc", **PARAMS, **kw)
    m.fit(M, y, sample_weight=w)
    state["names"] = names
    state["model"] = m
    return state
