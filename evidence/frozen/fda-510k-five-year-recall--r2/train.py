"""Self-contained XGBoost solution. Change this file; use evaluate.py to test.

Features are built only from the permitted predictor columns. Learned state
(category rates, counts) comes from the fitting partition only; training rows
receive out-of-fold target encodings so a row's own label never enters its
encoding (priors are computed on the same out-of-fold rows). Training row order
(chronological in the release) is used only inside fit, to form contiguous
folds and recency weights; prepare() is row-wise and order independent.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    "params": {"n_estimators": 400, "max_depth": 2, "learning_rate": 0.03,
               "subsample": 0.8, "colsample_bytree": 0.7, "min_child_weight": 5,
               "reg_lambda": 5.0, "gamma": 0.0},
    "te": [("product_code",), ("advisory_committee",), ("applicant_country_code",),
           ("product_code", "clearance_type")],
    "te_m": 20.0,
    "te_parent": {},     # child "a|b" -> parent "c|d": parent's shrunk rate is the child's prior
    "te_hidden": [],     # parents that are not emitted as features
    "te_decay": 0.0,     # label-stat weight = exp(te_decay * (rank - 1))
    "folds": 5,
    "fold_mode": "ordered",  # random | block (contiguous chronological blocks) | ordered (past blocks only)
    "blocks": 20,        # ordered mode: number of chronological blocks
    "drop_first": 2,     # ordered mode: leading blocks excluded from model fitting (no history)
    "te_n": False,       # emit the (weighted) history count behind each plain target encoding
    "te_random": False,  # hybrid: plain TE features from random K-fold OOF, kernel features ordered
    "lag_max": 0,        # ordered mode: per-row random extra staleness in blocks (0..lag_max)
    "kdecay": 5.0,       # recency decay for kernel-TE label stats
    "counts": [("product_code",)],
    # Raw columns left out after leave-one-out ablation showed no loss on validation or backtest.
    "drop": ["review_days", "device_class", "clearance_type", "third_party_flag", "ac_code", "is_us"],
    "recency": 0.0,      # sample weight = exp(recency * (rank - 1)), rank in [0, 1] by training row order
    "pc_letters": False,
    # Kernel target encodings over applicant_prior_clearances within a group: smoothed training
    # recall rate (and row count) among rows of the group with count in [n*(1-a)-b, n+up].
    "kte": [{"a": 0.3, "b": 3, "m": 5, "grp": "country_ac", "cnt": True},
            {"a": 0.3, "b": 3, "m": 5, "grp": "country_pc", "cnt": True}],
    "pc_aggs": False,    # label-free product-code aggregates
    "pc_time": False,    # label-free product-code first/last seen rank and recent volume
}

CAT_MAPS = {
    "device_class": {"1": 1.0, "2": 2.0, "3": 3.0, "U": 0.0},
    "clearance_type": {"Traditional": 0.0, "Special": 1.0, "Abbreviated": 2.0},
    "third_party_flag": {"N": 0.0, "Y": 1.0},
}


def _key(X, cols):
    k = X[cols[0]].astype("string").fillna("<NA>").astype(object)
    for c in cols[1:]:
        k = k + "|" + X[c].astype("string").fillna("<NA>").astype(object)
    return k.to_numpy()


def _grp(X, mode):
    c = X["applicant_country_code"].astype("string").fillna("<NA>").astype(object).to_numpy()
    if mode == "all":
        return np.array(["all"] * len(X), dtype=object)
    if mode == "us":
        return np.where(c == "US", "US", "non-US").astype(object)
    if mode == "country_ac":
        return c + "|" + X["advisory_committee"].astype("string").fillna("<NA>").astype(object).to_numpy()
    if mode == "country_pc":
        return c + "|" + X["product_code"].astype("string").fillna("<NA>").astype(object).to_numpy()
    if mode == "country_pc_ct":
        return (c + "|" + X["product_code"].astype("string").fillna("<NA>").astype(object).to_numpy()
                + "|" + X["clearance_type"].astype("string").fillna("<NA>").astype(object).to_numpy())
    if mode == "country_tp":
        return c + "|" + X["third_party_flag"].astype("string").fillna("<NA>").astype(object).to_numpy()
    if mode == "country_ct":
        return c + "|" + X["clearance_type"].astype("string").fillna("<NA>").astype(object).to_numpy()
    if mode == "ac":
        return X["advisory_committee"].astype("string").fillna("<NA>").astype(object).to_numpy()
    if mode == "pc":
        return X["product_code"].astype("string").fillna("<NA>").astype(object).to_numpy()
    return c


def _label_stats(cfg, X, y, rank):
    """All label-dependent statistics, from the rows given only."""
    rmax = float(rank.max()) if len(rank) else 1.0
    w = np.exp(cfg["te_decay"] * (rank - rmax)) if cfg["te_decay"] else np.ones(len(y))
    wk = np.exp(cfg["kdecay"] * (rank - rmax)) if cfg["kdecay"] else np.ones(len(y))
    prior = float((w * y).sum() / w.sum())
    st = {"prior": prior, "te": {}, "kte": []}
    for cols in list(cfg["te"]) + list(cfg["te_hidden"]):
        d = pd.DataFrame({"k": _key(X, cols), "s": w * y, "n": w}).groupby("k")[["s", "n"]].sum()
        st["te"]["|".join(cols)] = dict(zip(d.index, zip(d["s"].to_numpy(float), d["n"].to_numpy(float))))
    e = np.full(len(y), prior)
    if any(sp.get("oe") for sp in cfg["kte"]) and len(y):
        # Leave-one-out product_code rate: the row's own label is removed before smoothing.
        d = pd.DataFrame({"k": _key(X, ("product_code",)), "s": y, "n": 1.0})
        gs = d.groupby("k")[["s", "n"]].transform("sum")
        tot_s, tot_n = float(y.sum()), float(len(y))
        loo_prior = (tot_s - y) / max(1.0, tot_n - 1.0)
        e = (gs["s"].to_numpy() - y + cfg["te_m"] * loo_prior) / (gs["n"].to_numpy() - 1.0 + cfg["te_m"])
    rd = np.log1p(X["review_days"].to_numpy(float))
    sp = (X["clearance_type"].astype("string") == "Special").to_numpy(float)
    for spec in cfg["kte"]:
        g = _grp(X, spec["grp"])
        v = X["applicant_prior_clearances"].to_numpy(float)
        tab = {}
        if len(g):
            codes, names = pd.factorize(g)
            order = np.lexsort((v, codes))
            bounds = np.concatenate([[0], np.where(np.diff(codes[order]) != 0)[0] + 1, [len(order)]])
            for a0, a1 in zip(bounds[:-1], bounds[1:]):
                o = order[a0:a1]
                tab[names[codes[o[0]]]] = (v[o], np.concatenate([[0.0], np.cumsum(wk[o] * y[o])]),
                                           np.concatenate([[0.0], np.cumsum(wk[o])]),
                                           np.concatenate([[0.0], np.cumsum(wk[o] * e[o])]),
                                           np.concatenate([[0.0], np.cumsum(wk[o] * rd[o])]),
                                           np.concatenate([[0.0], np.cumsum(wk[o] * sp[o])]))
        st["kte"].append(tab)
    return st


def _label_feats(cfg, st, X):
    f = {}
    prior = st["prior"]
    m = cfg["te_m"]
    def enc(name):
        cols = tuple(name.split("|"))
        tab = st["te"][name]
        par = cfg["te_parent"].get(name)
        pr = enc(par) if par else np.full(len(X), prior)
        out = np.empty(len(X))
        for i, k in enumerate(_key(X, cols)):
            s, n = tab.get(k, (0.0, 0.0))
            out[i] = (s + m * pr[i]) / (n + m)
        return out
    for cols in cfg["te"]:
        f["te_" + "_".join(cols)] = enc("|".join(cols))
        if cfg["te_n"]:
            tab = st["te"]["|".join(cols)]
            f["ten_" + "_".join(cols)] = np.array([tab.get(k, (0.0, 0.0))[1] for k in _key(X, cols)])
    for j, spec in enumerate(cfg["kte"]):
        g = _grp(X, spec["grp"])
        v = X["applicant_prior_clearances"].to_numpy(float)
        out = np.empty(len(X))
        cnt = np.empty(len(X))
        oe = np.ones(len(X))
        xrd = np.full(len(X), np.nan)
        xsp = np.full(len(X), np.nan)
        gap = np.ones(len(X))
        c0 = spec["m"] * prior
        for i in range(len(X)):
            tab = st["kte"][j].get(g[i])
            if tab is None:
                out[i] = prior
                cnt[i] = 0.0
                continue
            lo = np.searchsorted(tab[0], v[i] * (1.0 - spec["a"]) - spec["b"], side="left")
            hi = np.searchsorted(tab[0], v[i] + spec.get("up", 0.0), side="right")
            if hi > 0:
                gap[i] = (v[i] - tab[0][min(hi, len(tab[0])) - 1]) / (v[i] + 1.0)
            s = tab[1][hi] - tab[1][lo]
            n = tab[2][hi] - tab[2][lo]
            out[i] = (s + spec["m"] * prior) / (n + spec["m"])
            cnt[i] = n
            oe[i] = (s + c0) / (tab[3][hi] - tab[3][lo] + c0)
            if n > 0:
                xrd[i] = (tab[4][hi] - tab[4][lo]) / n
                xsp[i] = (tab[5][hi] - tab[5][lo]) / n
        f["kte%d" % j] = out
        if spec.get("gap"):
            f["ktegap%d" % j] = gap
        if spec.get("extra"):
            f["kterd%d" % j] = xrd
            f["ktesp%d" % j] = xsp
            f["kterdrel%d" % j] = np.log1p(X["review_days"].to_numpy(float)) - xrd
        if spec.get("share") is not None:
            f["kteshare%d" % j] = cnt / (f["kten%d" % spec["share"]] + 1e-9) if spec.get("cnt") else cnt
        if spec.get("oe"):
            f["kteoe%d" % j] = oe
        if spec.get("ratio"):
            f["kter%d" % j] = np.log(out / f["te_" + spec["ratio"]])
        if spec.get("cnt"):
            f["kten%d" % j] = cnt
    return f


def _base(state, X):
    cfg = state["cfg"]
    f = {}
    f["review_days"] = X["review_days"].to_numpy(float)
    f["prior_clear"] = X["applicant_prior_clearances"].to_numpy(float)
    if cfg.get("coarse_prior"):
        f["prior_clear"] = np.floor(np.log2(1.0 + f["prior_clear"]) * cfg["coarse_prior"])
    for c, mp in CAT_MAPS.items():
        f[c] = X[c].astype("string").map(mp).astype(float).to_numpy()
    ac = X["advisory_committee"].astype("string")
    f["ac_code"] = ac.map(state["ac_codes"]).astype(float).to_numpy()
    f["is_us"] = (X["applicant_country_code"].astype("string") == "US").astype(float).to_numpy()
    for cols in cfg["counts"]:
        cnt = state["counts"]["|".join(cols)]
        f["cnt_" + "_".join(cols)] = np.array([cnt.get(k, 0.0) for k in _key(X, cols)])
    pck = _key(X, ("product_code",))
    if cfg["pc_letters"]:
        for j in range(3):
            f["pc_l%d" % j] = np.array([float(ord(k[j])) if len(k) == 3 else np.nan for k in pck])
    if cfg["pc_aggs"]:
        nan3 = (np.nan,) * 4
        a = np.array([state["pc_aggs"].get(k, nan3) for k in pck], dtype=float).reshape(len(X), 4)
        f["pc_mean_rd"] = a[:, 0]
        f["pc_mean_lpc"] = a[:, 1]
        f["pc_special"] = a[:, 2]
        f["pc_tp"] = a[:, 3]
        f["rd_rel"] = f["review_days"] - a[:, 0]
        f["lpc_rel"] = np.log1p(f["prior_clear"]) - a[:, 1]
    if cfg["pc_time"]:
        a = np.array([state["pc_time"].get(k, (np.nan, np.nan, 0.0)) for k in pck], dtype=float).reshape(len(X), 3)
        f["pc_first"] = a[:, 0]
        f["pc_last"] = a[:, 1]
        f["pc_recent"] = a[:, 2]
    return f


def _frame(state, f):
    return pd.DataFrame({c: np.asarray(f[c], dtype=float) for c in state["feature_names"]})


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    X = X_train.reset_index(drop=True)
    y = np.asarray(y_train).astype(float)
    n = len(X)
    rank = np.arange(n) / max(1, n - 1)
    state = {"cfg": cfg}
    state["ac_codes"] = {v: float(i) for i, v in enumerate(sorted(X["advisory_committee"].dropna().astype(str).unique()))}
    state["counts"] = {}
    for cols in cfg["counts"]:
        vc = pd.Series(_key(X, cols)).value_counts()
        state["counts"]["|".join(cols)] = {k: float(v) for k, v in vc.items()}
    pck = _key(X, ("product_code",))
    if cfg["pc_aggs"]:
        d = pd.DataFrame({"k": pck, "rd": X["review_days"].to_numpy(float),
                          "lpc": np.log1p(X["applicant_prior_clearances"].to_numpy(float)),
                          "sp": (X["clearance_type"].astype("string") == "Special").to_numpy(float),
                          "tp": (X["third_party_flag"].astype("string") == "Y").to_numpy(float)}).groupby("k").mean()
        state["pc_aggs"] = {k: tuple(float(x) for x in r) for k, r in zip(d.index, d.to_numpy())}
    if cfg["pc_time"]:
        d = pd.DataFrame({"k": pck, "r": rank})
        g = d.groupby("k").r.agg(["min", "max"])
        rec = d[d.r >= 0.8].groupby("k").size()
        state["pc_time"] = {k: (float(a), float(b), float(rec.get(k, 0.0))) for k, a, b in zip(g.index, g["min"], g["max"])}
    # Full-train label statistics (applied only to unseen rows in prepare).
    state["label"] = _label_stats(cfg, X, y, rank)
    # Out-of-fold label features for training rows.
    if cfg["fold_mode"] == "block":
        fold = np.minimum((rank * cfg["folds"]).astype(int), cfg["folds"] - 1)
    else:
        fold = np.random.RandomState(seed).randint(0, cfg["folds"], size=n)
    keep = np.ones(n, dtype=bool)
    nf = cfg["folds"]
    if cfg["fold_mode"] == "ordered":
        nf = cfg["blocks"]
        fold = np.minimum((rank * nf).astype(int), nf - 1)
        keep = fold >= cfg["drop_first"]
    oof = {}
    lag = np.zeros(n, dtype=int)
    if cfg["fold_mode"] == "ordered" and cfg["lag_max"]:
        lag = np.random.RandomState(seed + 1).randint(0, cfg["lag_max"] + 1, size=n)
    jobs = sorted(set(zip(fold.tolist(), lag.tolist())))
    for k, L in jobs:
        tr = np.where(fold < k - L)[0] if cfg["fold_mode"] == "ordered" else np.where(fold != k)[0]
        te = np.where((fold == k) & (lag == L))[0]
        if len(tr) == 0:
            tr = te[:0]
            st_k = {"prior": float(y.mean()), "te": {"|".join(c): {} for c in list(cfg["te"]) + list(cfg["te_hidden"])},
                    "kte": [{} for _ in cfg["kte"]]}
            for c, v in _label_feats(cfg, st_k, X.iloc[te]).items():
                oof.setdefault(c, np.empty(n))[te] = v
            continue
        st_k = _label_stats(cfg, X.iloc[tr], y[tr], rank[tr])
        for c, v in _label_feats(cfg, st_k, X.iloc[te]).items():
            oof.setdefault(c, np.empty(n))[te] = v
    if cfg["fold_mode"] == "ordered" and cfg["te_random"]:
        rf = np.random.RandomState(seed).randint(0, cfg["folds"], size=n)
        cfg_te = dict(cfg, kte=[])
        for k in range(cfg["folds"]):
            tr = np.where(rf != k)[0]
            te = np.where(rf == k)[0]
            st_k = _label_stats(cfg_te, X.iloc[tr], y[tr], rank[tr])
            for c, v in _label_feats(cfg_te, st_k, X.iloc[te]).items():
                oof[c][te] = v
    f = _base(state, X)
    f.update(oof)
    state["feature_names"] = [c for c in f.keys() if c not in set(cfg.get("drop", []))]
    w = np.exp(cfg["recency"] * (rank - 1.0)) if cfg["recency"] else None
    extra = {}
    if cfg.get("mono"):
        extra["monotone_constraints"] = tuple(
            1 if (c.startswith("te_") or (c.startswith("kte") and c[3:].isdigit())) else 0 for c in state["feature_names"])
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads,
                          eval_metric="logloss", **extra, **cfg["params"])
    F = _frame(state, f)
    if not keep.all():
        F, y, w = F[keep], y[keep], (w[keep] if w is not None else None)
    m.fit(F, y, sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    X = X.reset_index(drop=True)
    f = _base(state, X)
    f.update(_label_feats(state["cfg"], state["label"], X))
    return _frame(state, f)


def predict(model, X):
    return model["model"].predict_proba(prepare(model, X))[:, 1]
