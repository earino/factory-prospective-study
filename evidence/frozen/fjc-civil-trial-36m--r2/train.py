"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    # raw-derived numeric features (see _raw)
    "num": ["juris", "circuit", "demanded", "jury", "arbit", "res_p", "res_d", "nos10"],
    # features passed to XGBoost as native categoricals (integer codes learned on train)
    "cat": ["district", "nos"],
    # out-of-fold smoothed target encodings: list of key tuples
    "te": [],
    "te_m": 50.0,
    "te_folds": 5,
    # training-frequency encodings (share of training rows): list of key tuples
    "freq": [],
    # cap on effective rows per (district, nos, filing month) cell; None disables weights
    "cell_cap": 100,
    # exponential recency weights on training rows: exp(-(months before last training month)/tau); None disables
    "decay_tau": None,
    # unseen numeric categorical codes (e.g. a new NOS sub-code) fall back to the nearest training code
    "nearest": [],
    # key of the mass-filing cell used with cell_cap (filing month "_ym" optional)
    "cell_key": ("district", "nos", "_ym"),
    # 100 boosting rounds of 4 bagged trees each (row/column subsampled) inside one XGBClassifier
    "params": {"n_estimators": 100, "max_depth": 7, "learning_rate": 0.1, "min_child_weight": 5,
               "num_parallel_tree": 4, "subsample": 0.7, "colsample_bynode": 0.5},
}

_JURY = {"N": 0, "P": 1, "D": 2, "B": 3}
_ARBIT = {"M": 0, "V": 1, "E": 2, "Y": 3}


def _s(col):
    return col.astype(str).str.strip()


def _raw(X):
    """Row-wise deterministic recoding of the released predictors. No learned state."""
    n = len(X)
    d = {}
    nos = pd.to_numeric(X["NOS"], errors="coerce").to_numpy(dtype=float)
    d["nos"] = nos
    d["nos10"] = np.floor(nos / 10.0)
    d["nos100"] = np.floor(nos / 100.0)
    d["juris"] = pd.to_numeric(X["JURIS"], errors="coerce").to_numpy(dtype=float)
    d["circuit"] = pd.to_numeric(X["CIRCUIT"], errors="coerce").to_numpy(dtype=float)
    dem = pd.to_numeric(X["DEMANDED"], errors="coerce").to_numpy(dtype=float)
    d["demanded"] = dem
    d["dem_zero"] = (dem == 0).astype(float)
    d["dem_top"] = (dem >= 9999).astype(float)
    jury = _s(X["JURY"]).str.upper()
    d["jury"] = jury.map(_JURY).to_numpy(dtype=float)
    d["jury_any"] = jury.isin(["P", "D", "B"]).to_numpy(dtype=float)
    d["jury_def"] = jury.isin(["D", "B"]).to_numpy(dtype=float)
    d["arbit"] = _s(X["ARBIT"]).str.upper().map(_ARBIT).to_numpy(dtype=float)
    res = pd.to_numeric(X["RESIDENC"], errors="coerce").to_numpy(dtype=float)
    d["res"] = res
    d["res_p"] = np.floor(res / 10.0)
    d["res_d"] = res - 10.0 * np.floor(res / 10.0)
    ym = _s(X["FILEDATE_YEAR_MONTH"])
    d["year"] = pd.to_numeric(ym.str[:4], errors="coerce").to_numpy(dtype=float)
    d["moy"] = pd.to_numeric(ym.str[5:7], errors="coerce").to_numpy(dtype=float)
    dist = _s(X["DISTRICT"]).str.upper()
    dist = dist.where(~dist.str.fullmatch(r"\d"), "0" + dist)
    d["_district"] = dist.to_numpy(dtype=object)
    d["_ym"] = ym.to_numpy(dtype=object)
    d["_n"] = n
    return d


def _keycol(d, state, name):
    """Integer-valued (float) column usable as part of a group key; NaN -> -1."""
    if name == "district":
        v = pd.Series(d["_district"]).map(state["district_code"]).to_numpy(dtype=float)
    else:
        v = d[name]
    return np.where(np.isnan(v), -1.0, v).astype(np.int64)


def _key(d, state, names):
    k = np.zeros(d["_n"], dtype=np.int64)
    for nm in names:
        k = k * 100003 + (_keycol(d, state, nm) + 1)
    return k


def _te_fit(keys, y, m, folds, seed):
    n = len(y)
    rng = np.random.RandomState(seed)
    fold = rng.randint(0, folds, size=n)
    oof = np.empty(n, dtype=float)
    for f in range(folds):
        tr = fold != f
        prior = y[tr].mean()
        g = pd.DataFrame({"k": keys[tr], "y": y[tr]}).groupby("k")["y"].agg(["sum", "count"])
        s = pd.Series(keys[~tr]).map(g["sum"]).to_numpy(dtype=float)
        c = pd.Series(keys[~tr]).map(g["count"]).to_numpy(dtype=float)
        s = np.where(np.isnan(s), 0.0, s)
        c = np.where(np.isnan(c), 0.0, c)
        oof[~tr] = (s + m * prior) / (c + m)
    prior = float(y.mean())
    g = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    table = ((g["sum"] + m * prior) / (g["count"] + m)).to_dict()
    return oof, table, prior


def _matrix(state, d, te_override=None):
    cols = []
    for nm in state["num"]:
        cols.append(d[nm])
    for nm in state["cat"]:
        if nm == "district":
            v = pd.Series(d["_district"]).map(state["district_code"]).to_numpy(dtype=float)
        else:
            x = d[nm]
            if nm in state.get("nearest", ()):
                tv = state["cat_vals"][nm]
                j = np.clip(np.searchsorted(tv, x), 1, len(tv) - 1)
                lo, hi = tv[j - 1], tv[j]
                x = np.where(np.isnan(x), np.nan, np.where(np.abs(x - lo) <= np.abs(hi - x), lo, hi))
            v = pd.Series(x).map(state["cat_codes"][nm]).to_numpy(dtype=float)
        cols.append(v)
    for i, names in enumerate(state["te"]):
        if te_override is not None:
            cols.append(te_override[i])
        else:
            k = _key(d, state, names)
            v = pd.Series(k).map(state["te_tables"][i]).to_numpy(dtype=float)
            cols.append(np.where(np.isnan(v), state["te_priors"][i], v))
    for i, names in enumerate(state["freq"]):
        k = _key(d, state, names)
        v = pd.Series(k).map(state["freq_tables"][i]).to_numpy(dtype=float)
        cols.append(np.where(np.isnan(v), 0.0, v))
    return np.column_stack(cols).astype(np.float32)


def fit(X_train, y_train, *, seed, threads):
    cfg = CFG
    y = np.asarray(y_train).astype(int)
    d = _raw(X_train)
    state = {"num": list(cfg["num"]), "cat": list(cfg["cat"]), "te": [tuple(t) for t in cfg["te"]],
             "freq": [tuple(t) for t in cfg["freq"]], "nearest": list(cfg["nearest"]), "cat_vals": {}}
    state["district_code"] = {v: i for i, v in enumerate(sorted(set(d["_district"])))}
    state["cat_codes"] = {}
    for nm in state["cat"]:
        if nm != "district":
            vals = np.unique(d[nm][~np.isnan(d[nm])])
            state["cat_codes"][nm] = {float(v): i for i, v in enumerate(vals)}
            state["cat_vals"][nm] = np.asarray(vals, dtype=float)
    te_oof, state["te_tables"], state["te_priors"] = [], [], []
    for names in state["te"]:
        k = _key(d, state, names)
        oof, table, prior = _te_fit(k, y, cfg["te_m"], cfg["te_folds"], seed)
        te_oof.append(oof)
        state["te_tables"].append(table)
        state["te_priors"].append(prior)
    state["freq_tables"] = []
    for names in state["freq"]:
        k = _key(d, state, names)
        state["freq_tables"].append((pd.Series(k).value_counts() / len(k)).to_dict())
    M = _matrix(state, d, te_override=te_oof if state["te"] else None)
    w = None
    if cfg["cell_cap"]:
        ck = tuple(cfg["cell_key"])
        k = pd.Series(_key(d, state, tuple(c for c in ck if c != "_ym"))).astype(str)
        if "_ym" in ck:
            k = k + "|" + pd.Series(d["_ym"])
        cnt = k.map(k.value_counts()).to_numpy(dtype=float)
        w = np.minimum(1.0, cfg["cell_cap"] / cnt)
    if cfg.get("decay_tau"):
        t = d["year"] * 12.0 + d["moy"]
        t = np.where(np.isnan(t), np.nanmax(t), t)
        wd = np.exp(-(np.nanmax(t) - t) / float(cfg["decay_tau"]))
        w = wd if w is None else w * wd
    ftypes = ["q"] * len(state["num"]) + ["c"] * len(state["cat"]) + ["q"] * (len(state["te"]) + len(state["freq"]))
    names = (state["num"] + ["cat_" + c for c in state["cat"]] + ["te_" + "_".join(t) for t in state["te"]]
             + ["fr_" + "_".join(t) for t in state["freq"]])
    state["feature_names"] = names
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, feature_types=ftypes,
                          random_state=seed, n_jobs=threads, **cfg["params"])
    m.fit(M, y, sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    return _matrix(state, _raw(X))
