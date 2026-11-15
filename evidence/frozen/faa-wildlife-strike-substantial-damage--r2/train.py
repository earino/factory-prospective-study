"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    "params": {"n_estimators": 100, "max_depth": 6, "learning_rate": 0.1, "subsample": 0.8, "colsample_bytree": 0.8, "max_delta_step": 1, "reg_lambda": 20},
    "onehot": ["ac_class", "type_eng", "phase_of_flt", "warned", "time_of_day", "sky", "operator_class"],
    "state": "drop",          # drop | te | freq
    "engineered": False,
    "recency": 3.0,           # exponent strength of recency weights by training row order (0 = off)
    "min_count": 30,          # one-hot levels rarer than this in training are folded into "other"
    "te_folds": 5,
    "te_smooth": 50.0,
    "drop": [],
    "time_feat": False,       # train-only chronological rank feature, frozen to 1.0 ("now") at prediction
    "mono": {},               # feature name -> monotone constraint sign
    "eng_list": None,         # optional subset of engineered feature names
}

ORD = {
    "size": {"SMALL": 0.0, "MEDIUM": 1.0, "LARGE": 2.0},
    "birds_struck": {"0": 0.0, "1": 1.0, "2-10": 2.0, "11-100": 3.0, ">100": 4.0},
    "birds_seen": {"0": 0.0, "1": 1.0, "2-10": 2.0, "11-100": 3.0, ">100": 4.0},
}
NUM = ["ac_mass", "num_engs", "height_agl", "speed_kts", "distance_nm", "month"]
AIRBORNE = {"APPROACH": 1.0, "CLIMB": 1.0, "DESCENT": 1.0, "EN ROUTE": 1.0, "DEPARTURE": 1.0, "ARRIVAL": 1.0,
            "LOCAL": 1.0, "LANDING ROLL": 0.0, "TAKE-OFF RUN": 0.0, "TAXI": 0.0, "PARKED": 0.0}
CLIMBING = {"CLIMB": 1.0, "TAKE-OFF RUN": 1.0, "DEPARTURE": 1.0, "APPROACH": 0.0, "DESCENT": 0.0, "ARRIVAL": 0.0,
            "LANDING ROLL": 0.0, "TAXI": 0.0, "PARKED": 0.0, "LOCAL": 0.0, "EN ROUTE": 0.0}


def _col(X, c):
    return X[c].to_numpy(dtype=object)


def _map(v, d):
    return np.array([d.get(x, np.nan) for x in v], dtype=float)


def _features(state, X, te_override=None, t_override=None):
    cfg = state["cfg"]
    cols = {}
    for c in NUM:
        cols[c] = pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float)
    for c, d in ORD.items():
        cols[c] = _map(_col(X, c), d)
    for c in cfg["onehot"]:
        v = _col(X, c)
        for lv in state["levels"][c]:
            cols[c + "=" + lv] = np.array([1.0 if x == lv else 0.0 for x in v])
        cols[c + "=NA"] = np.array([1.0 if (x is None or x != x) else 0.0 for x in v])
    pv = _col(X, "precip")
    for tok in ["FOG", "RAIN", "SNOW"]:
        cols["precip_" + tok] = np.array([np.nan if (x is None or x != x) else float(tok in x) for x in pv])
    sv = _col(X, "state")
    if cfg["state"] == "te":
        cols["state_te"] = te_override if te_override is not None else _map(sv, state["state_te"])
    elif cfg["state"] == "freq":
        cols["state_freq"] = _map(sv, state["state_freq"])
    if cfg["engineered"]:
        ph = _col(X, "phase_of_flt")
        sp, sz, h, ms = cols["speed_kts"], cols["size"], cols["height_agl"], cols["ac_mass"]
        bs = cols["birds_struck"]
        cols["airborne"] = _map(ph, AIRBORNE)
        cols["climbing"] = _map(ph, CLIMBING)
        cols["energy"] = (sz + 1.0) * sp * sp
        cols["size_x_struck"] = (sz + 1.0) * bs
        cols["size_minus_mass"] = sz - ms
        cols["speed_per_mass"] = sp / ms
        cols["n_missing"] = np.sum(np.array([[1.0 if (x is None or x != x) else 0.0 for x in _col(X, c)]
                                             for c in state["raw_cols"]]), axis=0)
        m = cols["month"]
        cols["winter"] = np.abs(((m - 1.5) % 12) - 6.0)  # distance from mid-summer, peaks in Dec/Jan
    if cfg.get("eng_list") is not None and cfg["engineered"]:
        for k in ["airborne", "climbing", "energy", "size_x_struck", "size_minus_mass", "speed_per_mass", "n_missing", "winter"]:
            if k not in cfg["eng_list"]:
                cols.pop(k, None)
    if cfg.get("time_feat"):
        cols["t"] = np.full(len(X), 1.0) if t_override is None else t_override
    names = [n for n in state["names"]] if "names" in state else [n for n in cols if n not in cfg["drop"]]
    return pd.DataFrame({n: cols[n] for n in names}), names


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    y = np.asarray(y_train, dtype=float)
    n = len(y)
    state = {"cfg": cfg, "raw_cols": list(X_train.columns), "levels": {}}
    for c in cfg["onehot"]:
        vc = X_train[c].value_counts()
        state["levels"][c] = [str(k) for k, v in vc.items() if v >= cfg["min_count"]]
    te_oof = None
    sv = _col(X_train, "state")
    if cfg["state"] == "te":
        prior = float(y.mean())
        k = cfg["te_folds"]
        fold = np.random.RandomState(seed).randint(0, k, size=n)
        te_oof = np.full(n, np.nan)
        df = pd.DataFrame({"s": sv, "y": y, "f": fold})
        for f in range(k):
            a = df[df.f != f]
            pr = float(a.y.mean())
            g = a.groupby("s").y.agg(["sum", "count"])
            d = ((g["sum"] + cfg["te_smooth"] * pr) / (g["count"] + cfg["te_smooth"])).to_dict()
            idx = np.where(fold == f)[0]
            te_oof[idx] = [d.get(x, pr) for x in sv[idx]]
        g = df.groupby("s").y.agg(["sum", "count"])
        state["state_te"] = ((g["sum"] + cfg["te_smooth"] * prior) / (g["count"] + cfg["te_smooth"])).to_dict()
    elif cfg["state"] == "freq":
        state["state_freq"] = (pd.Series(sv).value_counts() / n).to_dict()
    # Training rows arrive in chronological file order; rank in that order is the only time proxy used.
    rank = np.arange(n) / max(1, n - 1)
    Z, names = _features(state, X_train, te_override=te_oof, t_override=rank)
    state["names"] = names
    w = None
    if cfg["recency"] > 0:
        w = np.exp(cfg["recency"] * (rank - 1.0))
    extra = {}
    if cfg.get("mono"):
        extra["monotone_constraints"] = "(" + ",".join(str(int(cfg["mono"].get(nm, 0))) for nm in names) + ")"
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, **cfg["params"], **extra)
    m.fit(Z, y, sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    return _features(state, X)[0]
