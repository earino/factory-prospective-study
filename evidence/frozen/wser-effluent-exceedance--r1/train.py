"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

CATS = ["reporting_frequency", "system_type", "owner_type_operator_type", "province",
        "treatment_family", "receiving_water_type"]
NUMS = ["prior_year_exceedance", "prior_year_worst_margin", "ever_exceeded_before",
        "history_years_reported", "periods_reported_prior_year", "avg_daily_effluent_volume_m3",
        "hydraulic_retention_ge_5_days", "chlorine_use", "prior_year_acute_lethality_failures"]

CFG = {
    "params": {"n_estimators": 800, "max_depth": 1, "learning_rate": 0.05, "subsample": 0.6,
               "colsample_bynode": 0.5, "colsample_bytree": 0.8, "min_child_weight": 20,
               "reg_lambda": 3, "reg_alpha": 0.1},
    "drop": ["prior_year_exceedance", "periods_reported_prior_year", "hydraulic_retention_ge_5_days", "reporting_frequency", "system_type", "receiving_water_type"],            # raw columns to exclude
    "cat_mode": "native",  # native | onehot | ordinal
    "extra": [],           # engineered feature names
    "mono": {},            # feature -> +1/-1
    "hist_cap": None,      # cap history_years_reported
    "w_nohist": 1.0,       # training weight for rows with no limit-based history at all
    "vol_impute": False,   # fill volume when missing although prior-year reports exist (train-median)
    "te": [("province", "reporting_frequency"), ("province", "marginbin"), ("treatment_family", "reporting_frequency")],              # list of column tuples for out-of-fold target encoding ("state" allowed)
    "te_m": 50.0,          # smoothing pseudo-count
    "te_folds": 5,
    "te_hier": False,      # shrink multi-column cells toward the first column's rate instead of the global rate
    "aug_mask": [],        # column groups; for each, append a copy of the training rows with them set missing
    "aug_w": 0.5,          # weight of each masked copy
    "aug_where": None,     # optional (column, value) restricting which rows are copied
    "additive": [],        # features barred from interacting with any other feature
    "groups": None,        # explicit interaction groups (lists of feature names); overrides additive
}


def _keys(X, combo):
    parts = []
    for c in combo:
        if c == "state":  # 2 exceeded last year, 1 earlier only, 0 never, NA unknown
            pye = X["prior_year_exceedance"].astype(float).to_numpy()
            eeb = X["ever_exceeded_before"].astype(float).to_numpy()
            v = np.where(pye == 1, "2", np.where(eeb == 1, "1", np.where(eeb == 0, "0", "NA")))
        elif c == "marginbin":  # severity class of last year's worst margin
            mm = X["prior_year_worst_margin"].astype(float).to_numpy()
            v = np.where(np.isnan(mm), "NA", np.digitize(np.nan_to_num(mm), [1e-9, 5.0, 20.0, 100.0]).astype(str))
        elif c == "volclass":  # log10 volume class
            vv = X["avg_daily_effluent_volume_m3"].astype(float).to_numpy()
            v = np.where(np.isnan(vv), "NA", np.floor(np.log10(np.maximum(np.nan_to_num(vv), 1.0))).astype(int).astype(str))
        else:
            v = X[c].astype(object).where(X[c].notna(), "NA").astype(str).to_numpy()
        parts.append(v.astype(object))
    k = parts[0]
    for p in parts[1:]:
        k = k + "|" + p
    return k


def _te_apply(keys, table, prior, m):
    s = np.array([table.get(k, (0.0, 0.0)) for k in keys], dtype=float).reshape(-1, 2)
    return (s[:, 0] + m * prior) / (s[:, 1] + m)


def _te_hier(X, combo, tables, prior, m):
    """Cell rate shrunk toward the (itself shrunk) rate of the first column of the key."""
    parent = _te_apply(_keys(X, combo[:1]), tables[1], prior, m)
    return _te_apply(_keys(X, combo), tables[0], parent, m)


def _te_table(keys, y):
    df = pd.DataFrame({"k": keys, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    return {k: (float(a), float(b)) for k, a, b in zip(df.index, df["sum"], df["count"])}


def _features(cfg, levels, X, te_override=None):
    out = {}
    drop = set(cfg["drop"])
    for c in NUMS:
        if c in drop:
            continue
        v = X[c].astype(float).to_numpy()
        if c == "history_years_reported" and cfg.get("hist_cap"):
            v = np.minimum(v, cfg["hist_cap"])
        out[c] = v
    ex = set(cfg["extra"])
    per = X["periods_reported_prior_year"].astype(float).to_numpy()
    freq = X["reporting_frequency"].astype(object).to_numpy()
    marg = X["prior_year_worst_margin"].astype(float).to_numpy()
    pye = X["prior_year_exceedance"].astype(float).to_numpy()
    eeb = X["ever_exceeded_before"].astype(float).to_numpy()
    hist = X["history_years_reported"].astype(float).to_numpy()
    vol = X["avg_daily_effluent_volume_m3"].astype(float).to_numpy()
    if cfg.get("vol_impute") and "avg_daily_effluent_volume_m3" in out:
        fill = np.isnan(vol) & (per > 0)
        out["avg_daily_effluent_volume_m3"] = np.where(fill, cfg["vol_fill"], vol)
        if cfg["vol_impute"] == "flag":
            out["vol_filled"] = fill.astype(float)
    if "region" in ex:  # coarse geography to pool small provinces
        reg = {"Alberta": 0.0, "Saskatchewan": 0.0, "Manitoba": 0.0, "British Columbia": 1.0, "Yukon": 1.0,
               "Ontario": 2.0, "Quebec": 3.0, "New Brunswick": 4.0, "Nova Scotia": 4.0,
               "Prince Edward Island": 4.0, "Newfoundland and Labrador": 5.0}
        out["region"] = np.array([reg.get(v, np.nan) for v in X["province"].astype(object).to_numpy()], dtype=float)
    if "ever_rate" in ex:  # lower bound on the past exceedance rate: 1/h if ever exceeded, else 0
        out["ever_rate"] = eeb / np.maximum(hist, 1.0)
    if "clean_years" in ex:  # reported years with no exceedance on record
        out["clean_years"] = np.where(eeb == 0, hist, np.where(eeb == 1, 0.0, np.nan))
    if "vol_bin" in ex:  # coarse volume class on a log10 scale
        out["vol_bin"] = np.floor(np.log10(np.maximum(vol, 1.0)))
    if "incomplete_q" in ex:  # quarterly reporter whose prior-year period count is not 4 or 12
        out["incomplete_q"] = ((freq == "quarterly") & ~np.isin(per, [4.0, 12.0])).astype(float)
    if "odd_periods" in ex:  # period count not one of the regular 1 / 4 / 12 schedules
        out["odd_periods"] = (~np.isin(per, [1.0, 4.0, 12.0])).astype(float)
    if "hist_state" in ex:  # 0 none ever, 1 past only, 2 last year; nan unknown
        hs = np.where(pye == 1, 2.0, np.where(eeb == 1, 1.0, np.where(eeb == 0, 0.0, np.nan)))
        out["hist_state"] = hs
    if "new_system" in ex:
        out["new_system"] = (hist <= 1).astype(float)
    if "no_prior" in ex:
        out["no_prior"] = np.isnan(pye).astype(float)
    if "log_margin" in ex:
        out["log_margin"] = np.log1p(marg)
    if "vol_per_period" in ex:
        out["vol_per_period"] = vol / np.maximum(per, 1.0)
    for i, combo in enumerate(cfg.get("te", [])):
        name = "te_" + "_".join(c[:6] for c in combo)
        if te_override is not None:
            out[name] = te_override[i]
        else:
            if cfg.get("te_hier") and len(combo) > 1:
                out[name] = _te_hier(X, combo, cfg["te_tables"][i], cfg["te_prior"], cfg["te_m"])
            else:
                out[name] = _te_apply(_keys(X, combo), cfg["te_tables"][i], cfg["te_prior"], cfg["te_m"])
    for c in CATS:
        if c in drop:
            continue
        lv = levels[c]
        codes = pd.Categorical(X[c], categories=lv).codes.astype(float)
        if cfg["cat_mode"] == "native":
            out[c] = pd.Categorical(X[c], categories=lv)
        elif cfg["cat_mode"] == "ordinal":
            out[c] = np.where(codes < 0, np.nan, codes)
        else:
            for i, l in enumerate(lv):
                out[f"{c}={i}"] = (codes == i).astype(float)
            out[f"{c}=NA"] = (codes < 0).astype(float)
    return pd.DataFrame(out)


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    levels = {c: pd.Index(sorted(X_train[c].dropna().unique())) for c in CATS}
    cfg["vol_fill"] = float(np.nanmedian(X_train["avg_daily_effluent_volume_m3"].to_numpy(dtype=float)))
    state = {"cfg": cfg, "levels": levels}
    te_oof = None
    if cfg.get("te"):
        y = np.asarray(y_train, dtype=float)
        n = len(y)
        fold = np.random.RandomState(seed).permutation(n) % cfg["te_folds"]
        te_oof, tables = [], []
        for combo in cfg["te"]:
            keys = _keys(X_train, combo)
            hier = bool(cfg.get("te_hier")) and len(combo) > 1
            pkeys = _keys(X_train, combo[:1]) if hier else None
            enc = np.zeros(n)
            for f in range(cfg["te_folds"]):
                tr_, ho_ = fold != f, fold == f
                # tables and priors all come from the other folds only (own label excluded)
                pr = y[tr_].mean()
                if hier:
                    pr = _te_apply(pkeys[ho_], _te_table(pkeys[tr_], y[tr_]), pr, cfg["te_m"])
                enc[ho_] = _te_apply(keys[ho_], _te_table(keys[tr_], y[tr_]), pr, cfg["te_m"])
            te_oof.append(enc)
            tables.append((_te_table(keys, y), _te_table(pkeys, y)) if hier else _te_table(keys, y))
        cfg["te_tables"], cfg["te_prior"] = tables, float(y.mean())
    Z = _features(cfg, levels, X_train, te_override=te_oof)
    params = dict(cfg["params"])
    if cfg["mono"]:
        params["monotone_constraints"] = "(" + ",".join(str(cfg["mono"].get(c, 0)) for c in Z.columns) + ")"
    cols = list(Z.columns)
    if cfg.get("groups"):
        params["interaction_constraints"] = [[c for c in g if c in cols] for g in cfg["groups"]]
    elif cfg.get("additive"):
        add = [c for c in cfg["additive"] if c in cols]
        params["interaction_constraints"] = [[c for c in cols if c not in add]] + [[c] for c in add]
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, random_state=seed,
                          n_jobs=threads, **params)
    w = np.where(X_train["ever_exceeded_before"].isna().to_numpy(), cfg.get("w_nohist", 1.0), 1.0)
    yy = np.asarray(y_train)
    if cfg.get("aug_mask"):
        Zs, ys, ws = [Z], [yy], [w]
        keep = np.ones(len(yy), dtype=bool)
        if cfg.get("aug_where"):
            keep = (X_train[cfg["aug_where"][0]] == cfg["aug_where"][1]).to_numpy()
        for grp in cfg["aug_mask"]:
            Xm = X_train[keep].copy()
            for c in grp:
                Xm[c] = np.nan
            Zs.append(_features(cfg, levels, Xm, te_override=None if te_oof is None else [e[keep] for e in te_oof]))
            ys.append(yy[keep]); ws.append(w[keep] * cfg["aug_w"])
        Z = pd.concat(Zs, ignore_index=True)
        for c in Z.columns:  # concat keeps categorical dtype only if categories agree; re-assert
            if c in levels and cfg["cat_mode"] == "native":
                Z[c] = pd.Categorical(Z[c], categories=levels[c])
        yy, w = np.concatenate(ys), np.concatenate(ws)
    m.fit(Z, yy, sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    return _features(state["cfg"], state["levels"], X)


def predict(model, X):
    return model["model"].predict_proba(prepare(model, X))[:, 1]
