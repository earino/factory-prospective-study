"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    # native categorical columns (integer codes, unseen -> NaN)
    "cat": ["NOS", "DISTRICT", "JURY", "JURIS"],
    # numeric raw / derived columns
    "num": ["DEMANDED"],
    # out-of-fold target encodings (tuples of raw columns)
    "te": [],
    # training-frequency encodings (tuples of raw columns)
    "freq": [],
    "te_smooth": 50.0,
    "te_folds": 5,
    # recency weighting: weight = decay ** (months before last training month / 12)
    "decay": 1.0,
    # weight multiplier for rows in very large (DISTRICT, NOS, YEAR_MONTH) filing clusters
    "cluster_cap": 0,
    # categorical levels with fewer training rows than this share one "other" code; unseen levels also map there
    "rare_min": 0,
    # optional per-feature sampling weights for colsample_bynode
    "fw": None,
    # unseen NOS code at prediction time -> nearest training NOS code in the same tens group (e.g. 835 -> 830)
    "nos_fallback": True,
    "params": {"n_estimators": 600, "max_depth": 5, "learning_rate": 0.03, "subsample": 0.8,
               "colsample_bynode": 0.6, "min_child_weight": 5},
}

RAW = ["NOS", "JURIS", "DISTRICT", "CIRCUIT", "JURY", "DEMANDED", "FILEDATE_YEAR_MONTH", "RESIDENC", "ARBIT"]


def _raw(X):
    """Column -> python list of normalised string/number values (row independent)."""
    r = {}
    for c in RAW:
        v = X[c].tolist()
        if c == "DEMANDED":
            r[c] = [_f(x) for x in v]
        else:
            r[c] = [_s(x) for x in v]
    return r


def _f(x):
    """Number or NaN; a non-numeric token such as 'MISSING' becomes NaN instead of raising."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def _s(x):
    """Text key for a code; an integer-valued float (column read as float) keys like the integer."""
    if isinstance(x, float) and x == x and x == int(x):
        return str(int(x))
    return str(x)


def _num(name, r):
    nan = float("nan")
    if name == "DEMANDED":
        return r["DEMANDED"]
    if name == "DEM_POS":
        return [1.0 if x > 0 else 0.0 for x in r["DEMANDED"]]
    if name == "DEM_TOP":
        return [1.0 if x >= 9999 else 0.0 for x in r["DEMANDED"]]
    if name == "MONTH":
        return [float(s[5:7]) for s in r["FILEDATE_YEAR_MONTH"]]
    if name == "YEAR":
        return [float(s[0:4]) + (float(s[5:7]) - 1) / 12.0 for s in r["FILEDATE_YEAR_MONTH"]]
    if name == "NOS_NUM":
        return [float(s) for s in r["NOS"]]
    if name == "NOS_GRP":
        return [float(int(s) // 10) for s in r["NOS"]]
    if name == "NOS_100":
        return [float(int(s) // 100) for s in r["NOS"]]
    if name == "JURIS_NUM":
        return [float(s) for s in r["JURIS"]]
    if name == "CIRCUIT_NUM":
        return [float(s) for s in r["CIRCUIT"]]
    if name == "RES_P":
        return [float(s[0]) if s[:1].isdigit() else nan for s in r["RESIDENC"]]
    if name == "RES_D":
        return [float(s[1]) if s[:1].isdigit() and len(s) > 1 else nan for s in r["RESIDENC"]]
    if name == "JURY_ANY":
        return [0.0 if s == "N" else 1.0 for s in r["JURY"]]
    if name == "JURY_DEF":
        return [1.0 if s in ("B", "D") else 0.0 for s in r["JURY"]]
    if name == "JURY_PLT":
        return [1.0 if s in ("B", "P") else 0.0 for s in r["JURY"]]
    raise KeyError(name)


def _nos_fallback(v, lv, other):
    """Code for an unseen NOS value: nearest seen code within the same tens group, else `other`."""
    try:
        x = int(v)
    except ValueError:
        return other
    best = None
    for k in lv:
        if k[:1].isdigit() and int(k) // 10 == x // 10:
            d = (abs(int(k) - x), int(k))
            if best is None or d < best[0]:
                best = (d, lv[k])
    return other if best is None else best[1]


def _keys(cols, r):
    if len(cols) == 1:
        return r[cols[0]]
    return list(zip(*[r[c] for c in cols]))


def _te_table(keys, y, prior, smooth):
    s = pd.DataFrame({"k": keys, "y": y}).groupby("k", sort=False)["y"].agg(["sum", "count"])
    val = (s["sum"].to_numpy() + prior * smooth) / (s["count"].to_numpy() + smooth)
    return dict(zip(s.index.tolist(), val.tolist()))


def fit(X_train, y_train, *, seed, threads):
    cfg = CFG
    y = np.asarray(y_train).astype(float)
    n = len(y)
    r = _raw(X_train)
    state = {"cfg": cfg, "levels": {}, "te": {}, "freq": {}, "prior": float(y.mean())}
    for c in cfg["cat"]:
        vc = pd.Series(r[c]).value_counts()
        lv = sorted(vc.index[vc.to_numpy() >= cfg.get("rare_min", 0)].tolist())
        d = {v: float(i) for i, v in enumerate(lv)}
        if cfg.get("rare_min", 0):
            d["\x00other"] = float(len(lv))
        state["levels"][c] = d
    for cols in cfg["freq"]:
        k = _keys(cols, r)
        vc = pd.Series(k).value_counts()
        state["freq"][tuple(cols)] = dict(zip(vc.index.tolist(), np.log1p(vc.to_numpy()).tolist()))
    # full-data target encodings for prediction time
    for cols in cfg["te"]:
        state["te"][tuple(cols)] = _te_table(_keys(cols, r), y, state["prior"], cfg["te_smooth"])
    Z = prepare(state, X_train)
    # out-of-fold target encodings for training rows (a row's own label never enters its encoding)
    if cfg["te"]:
        names = _names(cfg)
        rng = np.random.RandomState(seed)
        fold = rng.randint(0, cfg["te_folds"], size=n)
        for cols in cfg["te"]:
            j = names.index("TE_" + "_".join(cols))
            k = np.array(["|".join(t) if isinstance(t, tuple) else t for t in _keys(cols, r)], dtype=object)
            col = np.empty(n, dtype=np.float32)
            for f in range(cfg["te_folds"]):
                tr = fold != f
                pr = float(y[tr].mean())
                tab = _te_table(k[tr], y[tr], pr, cfg["te_smooth"])
                col[~tr] = [tab.get(x, pr) for x in k[~tr]]
            Z[:, j] = col
    w = np.ones(n)
    ym = r["FILEDATE_YEAR_MONTH"]
    if cfg["decay"] != 1.0:
        t = np.array([int(s[0:4]) * 12 + int(s[5:7]) for s in ym], dtype=float)
        w = w * cfg["decay"] ** ((t.max() - t) / 12.0)
    if cfg["cluster_cap"]:
        k = pd.Series(["|".join(t) for t in zip(r["DISTRICT"], r["NOS"], ym)])
        cnt = k.map(k.value_counts()).to_numpy().astype(float)
        w = w * np.minimum(1.0, cfg["cluster_cap"] / cnt)
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, feature_types=_ftypes(cfg),
                          random_state=seed, n_jobs=threads, **cfg["params"])
    m.fit(Z, y.astype(int), sample_weight=w, feature_weights=cfg.get("fw"))
    state["model"] = m
    return state


def _names(cfg):
    return (["C_" + c for c in cfg["cat"]] + list(cfg["num"]) + ["TE_" + "_".join(c) for c in cfg["te"]]
            + ["FQ_" + "_".join(c) for c in cfg["freq"]])


def _ftypes(cfg):
    return ["c"] * len(cfg["cat"]) + ["q"] * (len(cfg["num"]) + len(cfg["te"]) + len(cfg["freq"]))


def prepare(state, X):
    cfg = state["cfg"]
    nan = float("nan")
    r = _raw(X)
    cols = []
    for c in cfg["cat"]:
        lv = state["levels"][c]
        other = lv.get("\x00other", nan)
        if c == "NOS" and cfg.get("nos_fallback"):
            cols.append([lv[v] if v in lv else _nos_fallback(v, lv, other) for v in r[c]])
        else:
            cols.append([lv.get(v, other) for v in r[c]])
    for c in cfg["num"]:
        cols.append(_num(c, r))
    for c in cfg["te"]:
        tab = state["te"][tuple(c)]
        pr = state["prior"]
        if len(c) == 1:
            cols.append([tab.get(v, pr) for v in r[c[0]]])
        else:
            cols.append([tab.get(v, pr) for v in _keys(c, r)])
    for c in cfg["freq"]:
        tab = state["freq"][tuple(c)]
        cols.append([tab.get(v, 0.0) for v in _keys(c, r)])
    return np.array(cols, dtype=np.float32).T.reshape(len(X), len(cols))


def predict(model, X):
    return model["model"].predict_proba(prepare(model, X))[:, 1]
