"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    "cat_mode": "ordinal",     # onehot | ordinal | none
    "state_mode": "te",        # drop | onehot | te
    "min_level": 30,           # one-hot levels need at least this many training rows
    "engineered": True,
    "drop": [],
    "mono": {},
    "te_folds": 5,
    "te_smooth": 50.0,
    # Drift handling. Training rows arrive in chronological order (release sorts by date, id), so the
    # row rank is a recency proxy usable at FIT time only. No date/rank is used at prediction time.
    "recency_tau": None,       # exp sample-weight decay length as a fraction of training rows
    "window": None,            # keep only the most recent fraction of training rows
    "era": "free",             # None | "free" | "additive": training-rank feature, constant at predict
    "era_bins": None,          # if set, era is quantized to this many equal-count bins of training rank
    "era_predict": 1.0,        # era value assigned to every row at prediction time
    "keep": ["trainspeed", "hazmatcars", "hazmat_share", "energy", "hazmat_speed", "accidenttype", "tracktype",
             "trackclass_num", "loaded_frac", "state_te", "equipmenttype", "tons_per_car", "hazmat_per_loaded",
             "share_speed", "totalcars", "grosstonnage"],   # explicit feature whitelist (era is always kept)
    "era_with": None,          # if set (list), era may interact only with these features
    "extra": ["share_speed"],  # optional extra interaction features (see _base)
    # Covariate-shift weights learned on training rows only: an auxiliary out-of-fold classifier separates
    # the most recent `shift_frac` of training rows from older ones; rows get odds weights clipped to
    # [1/shift_clip, shift_clip]. The auxiliary model only produces sample weights and is not kept.
    "te_tau": None,            # recency decay (fraction of training rows) for target-encoding counts
    "tons_nan": True,          # treat grosstonnage == 0 as missing (not reported)
    "combo_te": False,         # OOF target encoding of accidenttype|tracktype|equipmenttype
    "shift_frac": None,
    "shift_clip": 5.0,
    "shift_power": 1.0,
}
PARAMS = {"n_estimators": 500, "max_depth": 2, "learning_rate": 0.03, "subsample": 0.8,
          "colsample_bytree": 0.6, "min_child_weight": 5, "reg_lambda": 5.0}

NUM = ["trainspeed", "hazmatcars", "loadedfreightcars", "emptyfreightcars", "grosstonnage", "temperature"]
CATS = ["equipmenttype", "tracktype", "weathercondition", "visibility", "accidenttype", "reporting_railroad_class"]


def _num(X, c):
    return pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float)


def _base(state, X):
    """Row-wise deterministic features; no statistics from the scoring batch."""
    cfg = state["cfg"]
    f = {}
    sp = _num(X, "trainspeed"); hz = _num(X, "hazmatcars"); ld = _num(X, "loadedfreightcars")
    em = _num(X, "emptyfreightcars"); gt = _num(X, "grosstonnage"); te = _num(X, "temperature")
    te = np.where((te < -60) | (te > 130), np.nan, te)
    if cfg.get("tons_nan"):
        gt = np.where(gt <= 0, np.nan, gt)
    f["trainspeed"] = sp; f["hazmatcars"] = hz; f["loadedfreightcars"] = ld
    f["emptyfreightcars"] = em; f["grosstonnage"] = gt; f["temperature"] = te
    tc = pd.to_numeric(X["trackclass"].astype(object).where(X["trackclass"].notna(), None), errors="coerce").to_numpy(dtype=float)
    f["trackclass_num"] = tc
    f["trackclass_X"] = (X["trackclass"].astype(str).to_numpy() == "X").astype(float)
    if cfg["engineered"]:
        tot = ld + em
        f["totalcars"] = tot
        f["hazmat_share"] = hz / np.maximum(tot, 1.0)
        f["hazmat_per_loaded"] = hz / np.maximum(ld, 1.0)
        f["loaded_frac"] = ld / np.maximum(tot, 1.0)
        f["tons_per_car"] = gt / np.maximum(tot, 1.0)
        f["tons_zero"] = (gt <= 0).astype(float)
        f["energy"] = np.log1p(np.maximum(gt, 0.0) * sp * sp)
        f["hazmat_speed"] = hz * sp
        f["hazmat_excess"] = hz - tot
    ex = cfg.get("extra") or []
    if ex:
        tot = ld + em
        at = X["accidenttype"].astype(str).to_numpy(); tt = X["tracktype"].astype(str).to_numpy()
        der = (at == "Derailment").astype(float); main = (tt == "Main").astype(float)
        lim = np.select([tc == 1, tc == 2, tc == 3, tc == 4, tc == 5, tc >= 6], [10., 25., 40., 60., 80., 110.], default=np.nan)
        cand = {
            "share_speed": hz / np.maximum(tot, 1.0) * sp,
            "hz_energy": np.log1p(hz) * np.log1p(np.maximum(gt, 0.0) * sp * sp),
            "speed_derail": sp * der,
            "speed_main": sp * main,
            "hz_derail": hz * der,
            "speed_ratio": sp / lim,
            "overspeed": sp - lim,
            "hz_speed2": np.log1p(hz * sp * sp),
            "loaded_speed": ld * sp,
            "hz_tons": hz * gt / np.maximum(tot, 1.0),
            "derail_main": der + 2 * main,
            "cars_speed": tot * sp,
            "nonhaz_loaded": ld - hz,
            # tonnage is 0 (not reported) for ~1/5 of rows, mostly yard cuts: estimate from car counts
            "energy_imp": np.log1p(np.where(gt > 0, gt, 100.0 * ld + 30.0 * em) * sp * sp),
            "tons_imp": np.where(gt > 0, gt, 100.0 * ld + 30.0 * em),
        }
        for k in ex:
            f[k] = cand[k]
    for c in CATS:
        v = X[c].astype(object).where(X[c].notna(), "__NA__").astype(str).to_numpy()
        if cfg["cat_mode"] == "onehot":
            for lv in state["levels"][c]:
                f[c + "=" + lv] = (v == lv).astype(float)
        elif cfg["cat_mode"] == "ordinal":
            m = state["ord"][c]
            f[c] = np.array([m.get(x, np.nan) for x in v], dtype=float)
    sv = X["stateabbr"].astype(object).where(X["stateabbr"].notna(), "__NA__").astype(str).to_numpy()
    if cfg["state_mode"] == "onehot":
        for lv in state["state_levels"]:
            f["state=" + lv] = (sv == lv).astype(float)
    elif cfg["state_mode"] == "te":
        m = state["state_te"]; d = state["prior"]
        f["state_te"] = np.array([m.get(x, d) for x in sv], dtype=float)
    if cfg.get("combo_te"):
        ck = _combo(X)
        m = state["combo_te"]; d = state["prior"]
        f["combo_te"] = np.array([m.get(x, d) for x in ck], dtype=float)
    if cfg.get("era"):
        f["era"] = np.full(len(X), _era(cfg, float(cfg.get("era_predict", 1.0))), dtype=float)
    out = pd.DataFrame(f)
    if cfg.get("keep"):
        out = out[[c for c in out.columns if c in cfg["keep"] or c in ("era", "combo_te")]]
    return out.drop(columns=[c for c in cfg["drop"] if c in out.columns])


def _era(cfg, rank):
    b = cfg.get("era_bins")
    if not b:
        return rank
    return np.minimum(np.floor(np.asarray(rank, dtype=float) * b), b - 1) / (b - 1)


def _combo(X):
    g = lambda c: X[c].astype(object).where(X[c].notna(), "__NA__").astype(str)
    return (g("accidenttype") + "|" + g("tracktype") + "|" + g("equipmenttype")).to_numpy()


def _te_map(keys, y, smooth, prior, w=None):
    if w is None:
        w = np.ones(len(y))
    d = pd.DataFrame({"k": keys, "s": y * w, "c": w}).groupby("k")[["s", "c"]].sum()
    return ((d["s"] + smooth * prior) / (d["c"] + smooth)).to_dict()


def _oof_te(k, y, w, cfg, seed, salt):
    rng = np.random.RandomState(seed + salt)
    fold = rng.randint(0, cfg["te_folds"], size=len(y))
    enc = np.empty(len(y))
    for j in range(cfg["te_folds"]):
        a = fold != j
        pr = float(np.sum(y[a] * w[a]) / np.sum(w[a]))   # prior excludes the held-out fold
        m = _te_map(k[a], y[a], cfg["te_smooth"], pr, w[a])
        enc[~a] = [m.get(x, pr) for x in k[~a]]
    return enc


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    y = np.asarray(y_train).astype(int)
    state = {"cfg": cfg, "levels": {}, "ord": {}}
    for c in CATS:
        v = X_train[c].astype(object).where(X_train[c].notna(), "__NA__").astype(str)
        vc = v.value_counts()
        state["levels"][c] = sorted(vc[vc >= cfg["min_level"]].index.tolist())
        # ordinal: order levels by training frequency (label-free), most frequent = 0
        state["ord"][c] = {k: i for i, k in enumerate(vc[vc >= cfg["min_level"]].index.tolist())}
    sv = X_train["stateabbr"].astype(object).where(X_train["stateabbr"].notna(), "__NA__").astype(str)
    vc = sv.value_counts()
    state["state_levels"] = sorted(vc[vc >= cfg["min_level"]].index.tolist())
    n0 = len(y)
    r0 = np.arange(n0, dtype=float) / max(n0 - 1, 1)
    tw = np.exp(-(1.0 - r0) / float(cfg["te_tau"])) if cfg.get("te_tau") else np.ones(n0)
    tw = tw / tw.mean()
    state["prior"] = float(np.sum(y * tw) / np.sum(tw))
    state["state_te"] = _te_map(sv.to_numpy(), y, cfg["te_smooth"], state["prior"], tw)
    state["combo_te"] = _te_map(_combo(X_train), y, cfg["te_smooth"], state["prior"], tw) if cfg.get("combo_te") else {}
    Z = _base(state, X_train)
    # out-of-fold encodings for training rows: each row's encoding (and prior) excludes its own fold
    if cfg["state_mode"] == "te" and "state_te" in Z.columns:
        Z["state_te"] = _oof_te(sv.to_numpy(), y, tw, cfg, seed, 0)
    if cfg.get("combo_te") and "combo_te" in Z.columns:
        Z["combo_te"] = _oof_te(_combo(X_train), y, tw, cfg, seed, 7)
    state["columns"] = list(Z.columns)
    n = len(y)
    rank = np.arange(n, dtype=float) / max(n - 1, 1)   # 0 = oldest training row, 1 = newest
    if cfg.get("era"):
        Z["era"] = _era(cfg, rank)
    w = np.ones(n)
    if cfg.get("recency_tau"):
        w = np.exp(-(1.0 - rank) / float(cfg["recency_tau"]))
        w = w / w.mean()
    if cfg.get("shift_frac"):
        fr = float(cfg["shift_frac"])
        d = (rank >= 1.0 - fr).astype(int)
        A = Z[[c for c in state["columns"] if c not in ("era", "state_te")]]
        fold = np.random.RandomState(seed + 1).randint(0, 5, size=n)
        pr = np.zeros(n)
        for j in range(5):
            a = fold != j
            dm = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, n_estimators=150,
                                   max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8)
            dm.fit(A[a], d[a])
            pr[~a] = dm.predict_proba(A[~a])[:, 1]
        pr = np.clip(pr, 1e-3, 1 - 1e-3)
        odds = pr / (1 - pr) * (1 - fr) / fr
        c = float(cfg["shift_clip"])
        sw = np.clip(odds, 1.0 / c, c) ** float(cfg.get("shift_power", 1.0))
        w = w * sw
        w = w / w.mean()
    keep = np.ones(n, dtype=bool)
    if cfg.get("window"):
        keep = rank >= 1.0 - float(cfg["window"])
    mono = cfg.get("mono") or {}
    kw = {}
    if cfg.get("era") and cfg.get("era_with") is not None:
        cols = state["columns"]
        kw["interaction_constraints"] = [[c for c in cols if c != "era"],
                                         ["era"] + [c for c in cols if c in cfg["era_with"]]]
    if cfg.get("era") == "additive":
        cols = state["columns"]
        kw["interaction_constraints"] = [[c for c in cols if c != "era"], ["era"]]
    if mono:
        kw["monotone_constraints"] = "(" + ",".join(str(int(mono.get(c, 0))) for c in state["columns"]) + ")"
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, **PARAMS, **kw)
    m.fit(Z[state["columns"]][keep], y[keep], sample_weight=w[keep])
    state["model"] = m
    return state


def prepare(state, X):
    return _base(state, X)[state["columns"]]
