"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    "params": {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.03, "subsample": 0.8,
               "colsample_bytree": 0.7, "min_child_weight": 5, "reg_lambda": 5.0},
    "cats": ["advisory_committee", "device_class", "clearance_type", "third_party_flag", "applicant_country_code"],
    "native_cat": False,
    "nums": ["review_days", "applicant_prior_clearances"],
    "counts": [("product_code",)],
    # target encodings: (key columns, parent key columns or None, smoothing)
    "te": [(("product_code",), None, 50.0), (("applicant_country_code",), None, 50.0),
           (("advisory_committee",), None, 50.0)],
    "nfold": 5,
    "fold_mode": "random",  # random | block (contiguous blocks of training row order = chronological blocks)
    # soft applicant-chain windows: (group key columns, rho, add, smoothing, emit_count)
    # rate of training labels among rows of the same group whose applicant_prior_clearances lies in [rho*c-add, c]
    "win": [(("applicant_country_code",), 0.7, 2, 20.0, True),
            (("applicant_country_code", "advisory_committee"), 0.7, 2, 20.0, True),
            (("applicant_country_code", "product_code"), 0.7, 2, 20.0, True)],
    "win_mode": "forward",  # random | block | forward (only earlier chronological blocks)
    "win_nfold": 20,
    "gstats": [],         # label-free group stats: (key columns, value name)
    "rel": [],            # deviations: (key columns, value name) -> row value minus group mean
    "mono_te": True,      # monotone-increasing constraint on target-encoded columns
}


def _val(X, name):
    """Label-free numeric row values."""
    if name == "lrd":
        return np.log1p(X["review_days"].to_numpy(dtype=float))
    if name == "lapc":
        return np.log1p(X["applicant_prior_clearances"].to_numpy(dtype=float))
    if name == "special":
        return (X["clearance_type"].to_numpy() == "Special").astype(float)
    if name == "tp":
        return (X["third_party_flag"].to_numpy() == "Y").astype(float)
    if name == "us":
        return (X["applicant_country_code"].to_numpy() == "US").astype(float)
    if name == "new":
        return (X["applicant_prior_clearances"].to_numpy(dtype=float) == 0).astype(float)
    raise KeyError(name)


def _col(X, c):
    """String key array for a raw or derived column (row-wise computable)."""
    if c == "pcb":   # log2 bucket of applicant prior clearances
        v = X["applicant_prior_clearances"].to_numpy(dtype=float)
        return np.floor(np.log2(v + 1.0)).astype(int).astype(str)
    if c == "pcb4":
        v = X["applicant_prior_clearances"].to_numpy(dtype=float)
        return np.floor(2 * np.log2(v + 1.0)).astype(int).astype(str)
    if c == "rdb":
        v = X["review_days"].to_numpy(dtype=float)
        return np.floor(np.log2(v + 1.0)).astype(int).astype(str)
    if c == "pc2":
        return np.array([str(s)[:2] for s in X["product_code"].to_numpy()])
    s = X[c]
    return s.astype(object).where(s.notna(), "__NA__").astype(str).to_numpy()


def _keys(X, cols):
    k = _col(X, cols[0]).astype(object)
    for c in cols[1:]:
        k = k + "|" + _col(X, c).astype(object)
    return k


def _sc(keys, y):
    df = pd.DataFrame({"k": keys, "s": y, "c": 1.0}).groupby("k")[["s", "c"]].sum()
    return dict(zip(df.index, zip(df["s"].to_numpy(), df["c"].to_numpy())))


def _enc(tab, ptab, keys, pkeys, prior, sm):
    """Smoothed rate; prior is the global rate or a smoothed parent-group rate."""
    out = np.empty(len(keys))
    for i, k in enumerate(keys):
        p = prior
        if ptab is not None:
            ps, pc = ptab.get(pkeys[i], (0.0, 0.0))
            p = (ps + prior * sm) / (pc + sm)
        s, c = tab.get(k, (0.0, 0.0))
        out[i] = (s + p * sm) / (c + sm)
    return out


def _wtab(keys, cnt, y):
    """Per group: sorted prior-clearance counts and cumulative label sums."""
    df = pd.DataFrame({"k": keys, "c": cnt, "y": y}).sort_values(["k", "c"], kind="mergesort")
    out = {}
    for k, g in df.groupby("k", sort=False):
        out[k] = (g["c"].to_numpy(dtype=float), np.concatenate([[0.0], np.cumsum(g["y"].to_numpy(dtype=float))]))
    return out


def _wenc(tab, keys, cnt, rho, add, prior, sm):
    rate = np.empty(len(keys))
    num = np.zeros(len(keys))
    for i, k in enumerate(keys):
        t = tab.get(k) if tab is not None else None
        if t is None:
            rate[i] = prior
            continue
        c = cnt[i]
        lo = np.searchsorted(t[0], np.floor(c * rho) - add, "left")
        hi = np.searchsorted(t[0], c, "right")
        num[i] = hi - lo
        rate[i] = (t[1][hi] - t[1][lo] + prior * sm) / (hi - lo + sm)
    return rate, num


def _base(state, X):
    cfg = state["cfg"]
    cols = []
    for c in cfg["cats"]:
        m = state["codes"][c]
        cols.append(np.array([m.get(v, np.nan) for v in X[c].to_numpy()], dtype=float))
    for c in cfg["nums"]:
        cols.append(X[c].to_numpy(dtype=float))
    for kc in cfg["counts"]:
        cnt = state["counts"][kc]
        cols.append(np.array([cnt.get(v, 0) for v in _keys(X, kc)], dtype=float))
    for kc, name in cfg["gstats"]:
        tab = state["gstats"][(kc, name)]
        cols.append(np.array([tab.get(k, np.nan) for k in _keys(X, kc)], dtype=float))
    for kc, name in cfg["rel"]:
        tab = state["gstats"][(kc, name)]
        cols.append(_val(X, name) - np.array([tab.get(k, np.nan) for k in _keys(X, kc)], dtype=float))
    return cols


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    X = X_train.reset_index(drop=True)
    y = np.asarray(y_train, dtype=float)
    n = len(X)
    state = {"cfg": cfg}
    state["codes"] = {c: {v: i for i, v in enumerate(sorted(X[c].dropna().unique()))} for c in cfg["cats"]}
    state["counts"] = {kc: pd.Series(_keys(X, kc)).value_counts().to_dict() for kc in cfg["counts"]}
    state["gstats"] = {}
    for kc, name in list(cfg["gstats"]) + list(cfg["rel"]):
        state["gstats"][(kc, name)] = pd.Series(_val(X, name)).groupby(_keys(X, kc)).mean().to_dict()
    prior = float(y.mean())
    state["prior"] = prior
    # training encodings are out-of-fold: a row's own label never enters its encoding, parent rate or prior
    rng = np.random.RandomState(seed)
    fold = rng.permutation(n) % cfg["nfold"]
    if cfg["fold_mode"] == "block":
        fold = (np.arange(n) * cfg["nfold"]) // n
    enc_cols = []
    state["te"] = []
    for kc, pk, sm in cfg["te"]:
        keys = _keys(X, kc)
        pkeys = _keys(X, pk) if pk else None
        enc = np.empty(n)
        for f in range(cfg["nfold"]):
            tr = fold != f
            te = ~tr
            enc[te] = _enc(_sc(keys[tr], y[tr]), _sc(pkeys[tr], y[tr]) if pk else None,
                           keys[te], pkeys[te] if pk else None, float(y[tr].mean()), sm)
        enc_cols.append(enc)
        state["te"].append((_sc(keys, y), _sc(pkeys, y) if pk else None))
    state["win"] = []
    cnt = X["applicant_prior_clearances"].to_numpy(dtype=float)
    K = cfg["win_nfold"]
    wfold = rng.permutation(n) % K if cfg["win_mode"] == "random" else (np.arange(n) * K) // n
    for kc, rho, add, sm, emit in cfg["win"]:
        keys = _keys(X, kc)
        rate = np.empty(n)
        num = np.empty(n)
        for f in range(K):
            te = wfold == f
            tr = (wfold < f) if cfg["win_mode"] == "forward" else ~te
            pf = float(y[tr].mean()) if tr.any() else np.nan
            tab = _wtab(keys[tr], cnt[tr], y[tr]) if tr.any() else None
            rate[te], num[te] = _wenc(tab, keys[te], cnt[te], rho, add, pf, sm)
        enc_cols.append(rate)
        if emit:
            enc_cols.append(num)
        state["win"].append(_wtab(keys, cnt, y))
    n_te = len(cfg["te"])
    Z = np.column_stack(_base(state, X) + enc_cols)
    ft = None
    if cfg["native_cat"]:
        ft = ["c"] * len(cfg["cats"]) + ["q"] * (Z.shape[1] - len(cfg["cats"]))
    mono = None
    if cfg["mono_te"]:
        mono = tuple([0] * (Z.shape[1] - len(enc_cols)) + [1] * n_te + [0] * (len(enc_cols) - n_te))
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, feature_types=ft,
                          monotone_constraints=mono, enable_categorical=bool(cfg["native_cat"]), **cfg["params"])
    m.fit(Z, y_train)
    state["model"] = m
    return state


def prepare(state, X):
    cols = _base(state, X)
    for (kc, pk, sm), (tab, ptab) in zip(state["cfg"]["te"], state["te"]):
        cols.append(_enc(tab, ptab, _keys(X, kc), _keys(X, pk) if pk else None, state["prior"], sm))
    cnt = X["applicant_prior_clearances"].to_numpy(dtype=float)
    for (kc, rho, add, sm, emit), tab in zip(state["cfg"]["win"], state["win"]):
        rate, num = _wenc(tab, _keys(X, kc), cnt, rho, add, state["prior"], sm)
        cols.append(rate)
        if emit:
            cols.append(num)
    return np.column_stack(cols)
