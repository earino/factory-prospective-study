"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import re
import numpy as np
import pandas as pd
import xgboost as xgb

CFG = {
    "params": {"n_estimators": 300, "max_depth": 2, "learning_rate": 0.03, "subsample": 0.5,
               "colsample_bynode": 0.5, "num_parallel_tree": 10, "min_child_weight": 5, "reg_lambda": 5.0},
    "te_cols": [],             # out-of-fold smoothed target encodings (none: agency/state/topic TE drift out-of-time)
    "te_smooth": 30.0,
    "te_folds": 5,
    "cat_cols": [],            # native XGBoost categoricals (low cardinality only)
    "use_year": True,
    "drop": [],
    "keep": ["emp", "log_amt", "sttr", "sttr_nondod", "dod_lag", "dod_tnum", "dod_tlet", "dod_rel_q25"],
    "recency_tau": None,       # sample weight exp((year - max_year)/tau); None = uniform
    "te_weighted": False,
    "cell_fe": None,           # None or shrink in [0,1]: agency-year OOF rate as nuisance feature (see fit)
    "ref_lag": 0,              # 0: same-year amount reference in training; L>0: reference at least L years old
    "mix_recent": 0.0,         # exponent for reweighting agencies to their share in the last two training years
    "mono": {},                # monotone constraints by feature name
    "mask_emp": 0.10,          # training only: blank employee counts in agency-year cells with > 5% missing/zero counts
    "cell_presence": False,
    "clean_cells": None,       # None, or max share of missing/zero employee counts allowed in an agency-year cell
    "stale_weight": 1.0,       # sample weight for rows whose employee count is missing or zero (stale records)
    "min_year": None,          # drop training rows before this award year
}

_DOD = re.compile(r"^([A-Z]+)(\d{2})(\d|[A-Z])?-([A-Z]*)(\d+)")
_RAW_CATS = ["agency", "branch", "program", "state", "hubzone_owned", "women_owned",
             "socially_economically_disadvantaged"]


def _s(v):
    if v is None or (isinstance(v, float) and v != v):
        return ""
    return str(v).strip()


def _row_feats(r):
    """Engineered values for one record (dict of raw fields). Pure function of the row."""
    agency = _s(r.get("agency")); branch = _s(r.get("branch")); program = _s(r.get("program"))
    topic = _s(r.get("topic_code")).upper()
    year = float(r.get("award_year")) if r.get("award_year") == r.get("award_year") else np.nan
    amt = r.get("award_amount"); amt = float(amt) if amt == amt and amt is not None else np.nan
    emp = r.get("number_employees"); emp = float(emp) if emp == emp and emp is not None else np.nan
    f = {}
    f["award_year"] = year
    f["log_amt"] = np.log1p(amt) if amt == amt and amt >= 0 else np.nan
    f["amt_round1k"] = float(amt % 1000 == 0) if amt == amt else np.nan
    f["amt_mod1k"] = float(amt % 1000) if amt == amt else np.nan
    f["emp"] = emp
    f["emp_missing"] = float(emp != emp)
    f["amt_per_emp"] = np.log1p(amt / (emp + 1.0)) if amt == amt and emp == emp and amt >= 0 else np.nan
    f["sttr"] = float(program == "STTR")
    for c in ("hubzone_owned", "women_owned", "socially_economically_disadvantaged"):
        v = _s(r.get(c))
        f[c + "_n"] = {"Y": 1.0, "N": 0.0}.get(v, np.nan)
    f["is_dod"] = float(agency.endswith("DEFENSE")); f["is_hhs"] = float(agency.endswith("SERVICES"))
    f["is_nsf"] = float(agency.endswith("FOUNDATION"))
    f["is_navy"] = float(branch == "Navy"); f["is_army"] = float(branch == "Army"); f["is_af"] = float(branch == "Air Force")
    below = ((-amt) % 25000.0) if amt == amt else np.nan      # dollars below the next 25k multiple
    f["amt_below25k"] = below
    f["dod_below25k"] = below if agency.endswith("DEFENSE") else np.nan
    f["dod_near_cap"] = (float(0 < below < 1000) if amt == amt else np.nan) if agency.endswith("DEFENSE") else np.nan
    f["amt_9xx"] = float((amt % 1000) >= 900) if amt == amt else np.nan
    f["sttr_nondod"] = float(program == "STTR") if not agency.endswith("DEFENSE") else np.nan
    f["emp_c20"] = min(emp, 20.0) if emp == emp else np.nan
    f["emp_over20"] = np.log1p(max(emp - 20.0, 0.0)) if emp == emp else np.nan
    f["emp_pos"] = emp if emp == emp and emp > 0 else np.nan
    f["emp_cap"] = min(emp, 60.0) if emp == emp else np.nan
    f["log_emp"] = np.log1p(emp) if emp == emp and emp >= 0 else np.nan
    # topic-code structure
    f["topic_missing"] = float(topic == "")
    f["topic_len"] = float(len(topic)) if topic else np.nan
    lead = re.match(r"[A-Z]+", topic)
    lead = lead.group(0) if lead else ""
    num = re.search(r"\d+", topic)
    f["topic_num"] = float(num.group(0)[:6]) if num else np.nan
    f["topic_alpha"] = float(topic.isalpha()) if topic else np.nan
    f["topic_digit"] = float(topic.isdigit()) if topic else np.nan
    lag = cyc = tnum = np.nan; tlet = ""
    m = _DOD.match(topic)
    if m and agency.endswith("DEFENSE"):
        lag = year - (2000.0 + float(m.group(2)))
        c = m.group(3)
        cyc = (float(c) if c.isdigit() else 10.0 + (ord(c) - 65)) if c else 0.0
        tlet = m.group(4)
        tnum = float(m.group(5)[:6])
    f["dod_lag"] = lag; f["dod_cycle"] = cyc; f["dod_tnum"] = tnum
    f["dod_tlet"] = float(tlet != "") if m else np.nan
    # categorical keys
    if agency.endswith("DEFENSE"):
        tkey = "DOD|" + lead
    elif topic == "":
        tkey = agency + "|NA"
    elif topic.isalpha() or len(topic) <= 5:
        tkey = agency + "|" + topic
    else:
        tkey = agency + "|" + lead
    k = {"tkey": tkey, "ag_prog": agency + "|" + program, "ag_br": agency + "|" + branch}
    for c in _RAW_CATS:
        k[c] = _s(r.get(c))
    return f, k


def _frames(X):
    rows = X.to_dict("records")
    fs, ks = [], []
    for r in rows:
        f, k = _row_feats(r)
        fs.append(f); ks.append(k)
    return pd.DataFrame(fs), pd.DataFrame(ks)


def _te_map(keys, y, prior, smooth, w=None):
    w = np.ones(len(y)) if w is None else w
    g = pd.DataFrame({"k": keys, "wy": y * w, "w": w}).groupby("k")[["wy", "w"]].sum()
    return ((g["wy"] + prior * smooth) / (g["w"] + smooth)).to_dict()


def fit(X_train, y_train, *, seed, threads):
    cfg = CFG
    y = np.asarray(y_train).astype(float)
    F, K = _frames(X_train.reset_index(drop=True))
    n = len(y)
    state = {"cfg": {k: v for k, v in cfg.items()}, "te": {}, "freq": {}, "levels": {}}
    # reference amounts: agency median over the most recent two training years (drift-aware)
    yr = F["award_year"].to_numpy(); amt = X_train["award_amount"].to_numpy(dtype=float)
    recent = yr >= np.nanmax(yr) - 1
    ref = pd.DataFrame({"a": K["agency"][recent], "v": amt[recent]}).groupby("a")["v"].median().to_dict()
    state["amt_ref"] = ref
    state["amt_ref_all"] = float(np.nanmedian(amt[recent]))
    state["year_max"] = float(np.nanmax(yr))
    for c in ("state", "tkey"):
        state["freq"][c] = (K[c].value_counts() / n).to_dict()
    # label-free amount references per (agency|branch, award_year): quartiles of award_amount
    gref = {}
    d = pd.DataFrame({"g": K["ag_br"], "y": yr, "v": amt}).dropna()
    for (g, yy), v in d.groupby(["g", "y"])["v"]:
        if len(v) >= cfg.get("ref_min", 8):
            gref.setdefault(g, []).append((float(yy),) + tuple(float(x) for x in np.percentile(v, [25, 50, 75])))
    state["gref"] = {g: sorted(v) for g, v in gref.items()}
    # out-of-fold target encodings: each row's encoding excludes its own label (prior included)
    w = np.ones(n)
    if cfg.get("recency_tau"):
        w = np.exp((yr - np.nanmax(yr)) / cfg["recency_tau"])
        w = w / w.mean()
    empv = F["emp"].to_numpy(dtype=float)
    w = w * np.where((empv != empv) | (empv == 0), cfg.get("stale_weight", 1.0), 1.0)
    _stale = ((empv != empv) | (empv == 0)).astype(float)
    _cell = (K["agency"] + "|" + F["award_year"].astype(str)).to_numpy()
    state["stale_share"] = pd.Series(_stale).groupby(_cell).mean().to_dict()
    if cfg.get("mask_emp") is not None:
        # training only: blank the employee count for every row of a cell whose reporting is incomplete, so the
        # employee curve is learned from complete-reporting cells and the presence artefact cannot be used
        _share = pd.Series(_stale).groupby(_cell).transform("mean").to_numpy()
        F = F.copy(); F.loc[_share > cfg["mask_emp"], "emp"] = np.nan
    if cfg.get("clean_cells") is not None:
        # label-free data-quality filter: drop whole agency x award-year cells whose employee field is partly unreported
        stale = ((empv != empv) | (empv == 0)).astype(float)
        cellkey = K["agency"] + "|" + F["award_year"].astype(str)
        share = pd.Series(stale).groupby(cellkey.to_numpy()).transform("mean").to_numpy()
        w = w * (share <= cfg["clean_cells"])
    if cfg.get("min_year"):
        w = w * (yr >= cfg["min_year"])
    if cfg.get("mix_recent"):
        # label-free covariate-shift weights: agency share in the latest two training years / share overall
        ag = K["agency"]
        sh_all = ag.value_counts(normalize=True); sh_rec = ag[recent].value_counts(normalize=True)
        ratio = (sh_rec.reindex(sh_all.index).fillna(sh_all.min()) / sh_all).clip(0.25, 4.0)
        w = w * ag.map(ratio).to_numpy(dtype=float) ** cfg["mix_recent"]
        w = w / w.mean()
    tw = w if cfg.get("te_weighted") else np.ones(n)
    rng = np.random.RandomState(seed)
    fold = rng.permutation(n) % cfg["te_folds"]
    oof = {}
    for c in cfg["te_cols"]:
        col = np.full(n, np.nan)
        for j in range(cfg["te_folds"]):
            tr = fold != j
            prior = np.average(y[tr], weights=tw[tr])
            mp = _te_map(K[c][tr].to_numpy(), y[tr], prior, cfg["te_smooth"], tw[tr])
            col[~tr] = K[c][~tr].map(mp).fillna(prior).to_numpy()
        oof[c] = col
        prior = np.average(y, weights=tw)
        state["te"][c] = (_te_map(K[c].to_numpy(), y, prior, cfg["te_smooth"], tw), float(prior))
    if cfg.get("cell_fe") is not None:
        # nuisance absorption: out-of-fold agency x award-year conversion rate (own label excluded).
        cell = (K["agency"] + "|" + F["award_year"].astype(str)).to_numpy()
        if cfg.get("cell_presence"):
            # also split each cell by whether the employee count is reported (> 0): absorbs the back-fill level effect
            ev_ = F["emp"].to_numpy(dtype=float)
            cell = np.array([c + ("|P" if (e == e and e > 0) else "|M") for c, e in zip(cell, ev_)])
        col = np.full(n, np.nan)
        for j in range(cfg["te_folds"]):
            tr = fold != j
            prior = y[tr].mean()
            mp = _te_map(cell[tr], y[tr], prior, cfg["te_smooth"])
            col[~tr] = pd.Series(cell[~tr]).map(mp).fillna(prior).to_numpy()
        oof["__cell"] = col
        prior = float(y.mean())
        amap = _te_map(K["agency"].to_numpy(), y, prior, cfg["te_smooth"])
        state["cell"] = ({a: prior + cfg["cell_fe"] * (v - prior) for a, v in amap.items()}, prior)
    for c in cfg["cat_cols"]:
        vc = K[c].value_counts()
        state["levels"][c] = sorted(vc[vc >= 20].index.tolist())
    Z = _assemble(state, F, K, oof)
    state["cols"] = list(Z.columns)
    extra = {}
    if cfg.get("mono"):
        extra["monotone_constraints"] = tuple(int(cfg["mono"].get(c, 0)) for c in Z.columns)
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, random_state=seed, n_jobs=threads,
                          max_cat_to_onehot=1, **extra, **cfg["params"])
    m.fit(Z, y_train, sample_weight=w)
    state["model"] = m
    return state


def _assemble(state, F, K, oof=None):
    cfg = state["cfg"]
    Z = F.copy()
    ref = K["agency"].map(state["amt_ref"]).fillna(state["amt_ref_all"]).to_numpy(dtype=float)
    Z["amt_rel"] = np.log1p(np.exp(Z["log_amt"]) - 1.0 + 1.0) - np.log1p(ref)
    for c in ("state", "tkey"):
        Z["freq_" + c] = K[c].map(state["freq"][c]).fillna(0.0).to_numpy(dtype=float)
    q = np.full((len(Z), 3), np.nan)
    amt = np.expm1(Z["log_amt"].to_numpy(dtype=float)); yrs = F["award_year"].to_numpy(dtype=float)
    for i, g in enumerate(K["ag_br"].to_numpy()):
        lst = state["gref"].get(g)
        if lst and yrs[i] == yrs[i]:
            # reference year: the same year when seen in training, else the nearest earlier (or nearest) year
            lag = cfg.get("ref_lag", 0)
            if lag:
                # train-as-you-score: compare with a reference at least `lag` years old (else the earliest one)
                past = [e for e in lst if e[0] <= yrs[i] - lag]
                best = past[-1] if past else lst[0]
            else:
                best = min(lst, key=lambda e: (abs(e[0] - yrs[i]) + (0.5 if e[0] > yrs[i] else 0.0)))
            q[i] = best[1:]
    Z["amt_rel_q25"] = amt / q[:, 0]
    Z["amt_rel_q50"] = amt / q[:, 1]
    Z["amt_rel_q75"] = amt / q[:, 2]
    dod = F["is_dod"].to_numpy() == 1.0
    Z["dod_log_amt"] = np.where(dod, Z["log_amt"], np.nan)
    Z["nondod_log_amt"] = np.where(dod, np.nan, Z["log_amt"])
    Z["dod_rel_q25"] = np.where(dod, amt / q[:, 0], np.nan)
    Z["dod_rel_q50"] = np.where(dod, amt / q[:, 1], np.nan)
    Z["dod_rel_q75"] = np.where(dod, amt / q[:, 2], np.nan)
    # reporting-regime feature: share of unreported employee counts in the row's agency-year cell (0 for unseen cells)
    Z["cell_stale"] = (K["agency"] + "|" + F["award_year"].astype(str)).map(state["stale_share"]).fillna(0.0).to_numpy(dtype=float)
    hhs = F["is_hhs"].to_numpy() == 1.0
    Z["hhs_log_amt"] = np.where(hhs, Z["log_amt"], np.nan)
    Z["hhs_rel_q50"] = np.where(hhs, amt / q[:, 1], np.nan)
    Z["hhs_emp"] = np.where(F["is_hhs"].to_numpy() == 1.0, F["emp"], np.nan)
    Z["nsf_emp"] = np.where(F["is_nsf"].to_numpy() == 1.0, F["emp"], np.nan)
    Z["amt_iqr_pos"] = (amt - q[:, 0]) / np.where(q[:, 2] - q[:, 0] > 1000, q[:, 2] - q[:, 0], np.nan)
    for c in cfg["te_cols"]:
        if oof is not None:
            Z["te_" + c] = oof[c]
        else:
            mp, prior = state["te"][c]
            Z["te_" + c] = K[c].map(mp).fillna(prior).to_numpy(dtype=float)
    if cfg.get("cell_fe") is not None:
        if oof is not None:
            Z["cell_fe"] = oof["__cell"]
        else:
            mp, prior = state["cell"]
            Z["cell_fe"] = K["agency"].map(mp).fillna(prior).to_numpy(dtype=float)
    for c in cfg["cat_cols"]:
        Z["cat_" + c] = pd.Categorical(K[c], categories=state["levels"][c])
    if not cfg["use_year"]:
        Z = Z.drop(columns=["award_year"])
    Z = Z.drop(columns=[c for c in cfg["drop"] if c in Z.columns])
    if cfg.get("keep"):
        Z = Z[[c for c in Z.columns if c in cfg["keep"]]]
    return Z


def prepare(state, X):
    F, K = _frames(X)
    Z = _assemble(state, F, K)
    return Z[state["cols"]]


def predict(model, X):
    return model["model"].predict_proba(prepare(model, X))[:, 1]
