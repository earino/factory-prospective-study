"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    "cats": ["NOS", "DISTRICT", "JURY", "JURIS"],   # native categorical codes (RESIDENC, ARBIT, CIRCUIT dropped: H5)
    "nums": ["DEMANDED"],                                                          # raw numeric
    "derived": [],                                                                 # extra derived columns
    "te": [],                                                                      # target-encoded key tuples
    "te_m": 50.0, "te_folds": 5,
    "recency": 0.0,                                                                # weight slope over train period
    "nos_fallback": True,                                                          # unseen NOS -> nearest lower training code in same hundred
    "cellcap": 0,                                                                  # cap on effective rows per DISTRICT x NOS x month cell
    "params": {"n_estimators": 500, "max_depth": 6, "learning_rate": 0.03, "min_child_weight": 5,
               "subsample": 0.8, "colsample_bytree": 0.8, "colsample_bynode": 0.7, "num_parallel_tree": 3},
}

NOS_GROUP = [(110, 199, "contract"), (210, 299, "realprop"), (310, 369, "pi_tort"), (370, 389, "pp_tort"),
             (400, 400, "other"), (410, 430, "other"), (440, 449, "civrights"), (450, 499, "other"),
             (610, 699, "forfeit"), (710, 799, "labor"), (820, 840, "ip"), (850, 850, "securities"),
             (860, 869, "socsec"), (870, 875, "tax"), (890, 999, "otherstat")]


def _nos_group(n):
    for lo, hi, g in NOS_GROUP:
        if lo <= n <= hi:
            return g
    return "other"


def _raw(X):
    """Derived string/numeric columns as a dict of numpy arrays (vectorised; row-order independent)."""
    n = len(X)
    d = {}
    nos = X["NOS"].to_numpy()
    d["NOS"] = nos.astype(np.int64).astype(str)
    d["JURIS"] = X["JURIS"].to_numpy().astype(np.int64).astype(str)
    d["CIRCUIT"] = X["CIRCUIT"].to_numpy().astype(np.int64).astype(str)
    for c in ["DISTRICT", "JURY", "RESIDENC", "ARBIT"]:
        d[c] = X[c].astype(str).to_numpy()
    dem = X["DEMANDED"].to_numpy().astype(float)
    d["DEMANDED"] = dem
    d["DEM_POS"] = (dem > 0).astype(float)
    d["DEM_TOP"] = (dem >= 9999).astype(float)
    d["NOS_NUM"] = nos.astype(float)
    d["NOSG"] = np.array([_nos_group(int(v)) for v in nos], dtype=object).astype(str)
    d["NOS10"] = (nos.astype(np.int64) // 10).astype(str)
    res = d["RESIDENC"]
    d["RES_P"] = np.array([r[0] if r != "MISSING" and len(r) == 2 else "M" for r in res], dtype=object).astype(str)
    d["RES_D"] = np.array([r[1] if r != "MISSING" and len(r) == 2 else "M" for r in res], dtype=object).astype(str)
    d["JURYANY"] = np.array([0.0 if j == "N" else 1.0 for j in d["JURY"]])
    ym = X["FILEDATE_YEAR_MONTH"].astype(str).to_numpy()
    d["MOY"] = np.array([float(s[5:7]) for s in ym])
    d["YM"] = ym
    yr = np.array([float(s[0:4]) for s in ym])
    d["FY"] = yr + (d["MOY"] >= 10)                       # federal fiscal year of filing
    d["FYH"] = d["FY"] + 0.5 * ((d["MOY"] >= 4) & (d["MOY"] <= 9))   # fiscal half-year
    d["TIME"] = np.array([float(s[0:4]) + (float(s[5:7]) - 0.5) / 12.0 for s in ym])
    return d


def _nos_fallback(state, d):
    """Map a nature-of-suit code never seen in training to the closest training code below it in the same
    hundred-block of the codebook (e.g. a new sub-code 835 -> 830), using fitted state only."""
    codes = state.get("nos_codes")
    if not codes:
        return d
    known = state["nos_set"]
    out = d["NOS"].astype(object)
    for i, v in enumerate(out):
        if v not in known:
            n = int(v)
            same = [c for c in codes if c // 100 == n // 100]
            lower = [c for c in same if c < n]
            pick = max(lower) if lower else (min(same) if same else None)
            if pick is not None:
                out[i] = str(pick)
    d["NOS"] = out.astype(str)
    return d


def _key(d, cols):
    k = d[cols[0]].astype(object)
    for c in cols[1:]:
        k = k + "|" + d[c].astype(object)
    return k


def _te_apply(keys, table, prior, m):
    out = np.empty(len(keys))
    for i, k in enumerate(keys):
        s, c = table.get(k, (0.0, 0.0))
        out[i] = (s + prior * m) / (c + m)
    return out


def _te_table(keys, y):
    g = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    return {k: (float(s), float(c)) for k, s, c in zip(g.index, g["sum"], g["count"])}


def _matrix(state, d, te_cols=None):
    cfg = state["cfg"]
    cols = []
    for c in cfg["cats"]:
        lv = state["levels"][c]
        cols.append(np.array([lv.get(v, np.nan) for v in d[c]], dtype=float))
    for c in cfg["nums"] + cfg["derived"]:
        v = np.asarray(d[c], dtype=float)
        if c in state.get("clip_max", {}):
            v = np.minimum(v, state["clip_max"][c])       # later periods are scored as the last training period
        cols.append(v)
    for j, t in enumerate(cfg["te"]):
        if te_cols is not None:
            cols.append(te_cols[j])
        else:
            cols.append(_te_apply(_key(d, t), state["te_tables"][j], state["prior"], cfg["te_m"]))
    return np.column_stack(cols).astype(np.float32)


def fit(X_train, y_train, *, seed, threads, cfg=None):
    cfg = dict(CFG if cfg is None else cfg)
    y = np.asarray(y_train).astype(int)
    d = _raw(X_train)
    state = {"cfg": cfg, "prior": float(y.mean())}
    state["clip_max"] = {c: float(np.max(d[c])) for c in cfg["derived"] if c in ("FY", "FYH", "TIME")}
    if cfg.get("nos_fallback"):
        state["nos_set"] = set(d["NOS"])
        state["nos_codes"] = sorted(int(v) for v in state["nos_set"])
    state["levels"] = {c: {v: i for i, v in enumerate(sorted(set(d[c])))} for c in cfg["cats"]}
    # Out-of-fold target encodings for training rows (a row's own label never enters its encoding);
    # the stored tables for scoring use all training rows.
    rng = np.random.RandomState(seed)
    fold = rng.randint(0, cfg["te_folds"], size=len(y))
    te_cols, tables = [], []
    for t in cfg["te"]:
        k = _key(d, t)
        col = np.empty(len(y))
        for f in range(cfg["te_folds"]):
            tr, ho = fold != f, fold == f
            col[ho] = _te_apply(k[ho], _te_table(k[tr], y[tr]), float(y[tr].mean()), cfg["te_m"])
        te_cols.append(col)
        tables.append(_te_table(k, y))
    state["te_tables"] = tables
    M = _matrix(state, d, te_cols)
    ftypes = ["c"] * len(cfg["cats"]) + ["q"] * (len(cfg["nums"]) + len(cfg["derived"]) + len(cfg["te"]))
    w = None
    if cfg["recency"]:
        t = d["TIME"]
        w = 1.0 + cfg["recency"] * (t - t.min()) / max(1e-9, t.max() - t.min())
    if cfg.get("cellcap"):
        # Training-only weights: a filing-month cell of one district and nature of suit that is far larger
        # than the cap (mass-tort waves) contributes at most `cellcap` effective rows.
        k = _key(d, ("DISTRICT", "NOS", "YM"))
        cnt = pd.Series(k).map(pd.Series(k).value_counts()).to_numpy().astype(float)
        cw = np.minimum(1.0, cfg["cellcap"] / cnt)
        w = cw if w is None else w * cw
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, feature_types=ftypes,
                          random_state=seed, n_jobs=threads, **cfg["params"])
    m.fit(M, y, sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    return _matrix(state, _nos_fallback(state, _raw(X)))
