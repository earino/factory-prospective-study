"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {"n_estimators": 40, "num_parallel_tree": 10, "max_depth": 3, "learning_rate": 0.3, "subsample": 0.6,
          "colsample_bytree": 0.5, "colsample_bynode": 0.5, "min_child_weight": 3, "reg_lambda": 10.0,
          "max_bin": 16}
# feature groups: cost, review, miss, month, inter, combo
CFG = {"drop": ["cost_round1k", "issue_month_sin", "issue_month_cos", "description_length"], "groups": ["cost", "miss", "inter", "combo", "tz"], "mono": True, "min_level": 100,
       "mono_extra": {}, "additive": [], "impute_tdpr": False,
       "recode_review": True, "zip": "cat", "onehot": 64}
CATS = ["permitclass", "permitclassmapped", "permittypedesc", "originalzip"]
MONO = {"applied_to_issued_days": -1}


def _combo(X):
    sp = np.where(X["standardplan"].isna(), "spNA", "sp0")
    return X["permitclass"].astype("object").fillna("NA") + "|" + X["permittypedesc"].astype("object").fillna("NA") + "|" + sp


def _features(state, X):
    cfg = state["cfg"]
    g = cfg["groups"]
    out = pd.DataFrame(index=X.index)
    for c in state["num"]:
        out[c] = pd.to_numeric(X[c], errors="coerce").astype("float64")
    # standardplan is only ever 0 or blank in training; a recorded value of 1 (seen from mid-2019) must not be
    # routed like a blank by threshold splits, so the column is reduced to recorded (0) vs blank
    out["standardplan"] = out["standardplan"].where(out["standardplan"].isna(), 0.0)
    cost = out["estprojectcost"]
    a2i = out["applied_to_issued_days"]
    nrc = out["numberreviewcycles"]
    hua = out["housingunitsadded"]
    nrc_raw_missing = nrc.isna().to_numpy()
    if cfg.get("impute_tdpr"):
        # plan-review total is ~equal to applied->issued days when recorded; fill it when a reviewed permit lacks it
        fill = (out["totaldaysplanreview"].isna() & (a2i > 7)).to_numpy()
        out["tdpr_unrecorded"] = fill.astype("float64")
        out.loc[fill, "totaldaysplanreview"] = a2i[fill]
    if cfg["recode_review"]:
        # review counters are structurally 0/blank on records without a recorded plan-review total;
        # when such a permit still took >7 days to issue, treat the counters as unknown rather than zero
        unk = (out["totaldaysplanreview"].isna() & ~(nrc > 0) & (a2i > cfg.get("recode_days", 7))).to_numpy()
        if "miss" in g:
            out["review_unrecorded"] = unk.astype("float64")
        out.loc[unk, ["numberreviewcycles", "daysoutcorrections"]] = np.nan
        nrc = out["numberreviewcycles"]
    is_new = (X["permittypedesc"] == "New").to_numpy()
    sp_miss = X["standardplan"].isna().to_numpy()
    if "cost" in g:
        out["cost_round1k"] = (cost % 1000 == 0).astype("float64")
        units = out["housingunits"]
        out["cost_per_unit"] = cost / units.where(units > 0)
    if "review" in g:
        out["otc"] = (a2i <= 1).astype("float64")
        out["doc_share"] = out["daysoutcorrections"] / a2i.where(a2i > 0)
        out["city_days"] = a2i - out["daysoutcorrections"].fillna(0)
        out["days_per_cycle"] = a2i / nrc.where(nrc > 0)
    if "miss" in g:
        out["hu_missing"] = hua.isna().astype("float64")
        out["sp_missing"] = sp_miss.astype("float64")
        out["nrc_missing"] = nrc_raw_missing.astype("float64")
    if "month" in g:
        out["month"] = np.round((np.degrees(np.arctan2(out["issue_month_sin"], out["issue_month_cos"])) % 360) / 30.0)
    if "inter" in g:
        out["new_sp_missing"] = (is_new & sp_miss).astype("float64")
        out["new_no_units"] = (is_new & ~(hua.to_numpy() > 0)).astype("float64")
        out["new_units"] = np.where(is_new, hua.fillna(-1).to_numpy(), -2.0)
    if "gap" in g:
        out["issue_gap"] = a2i - out["totaldaysplanreview"]
        out["doc_per_cycle"] = out["daysoutcorrections"] / nrc.where(nrc > 0)
    if "tz" in g:
        ci = cost.fillna(0).round().astype("int64")
        tz = pd.Series(0.0, index=X.index)
        for k in range(1, 7):
            tz = tz + (ci % (10 ** k) == 0).astype("float64")
        out["cost_trailing_zeros"] = tz
    if "tzx" in g:
        ci2 = cost.fillna(0).round().astype("int64")
        rnd = (ci2 % 1000 == 0).to_numpy()
        mup = (out["related_mup_flag"] == 1).to_numpy()
        out["new_round_cost"] = (is_new & rnd).astype("float64")
        out["mup_round_cost"] = (mup & rnd).astype("float64")
        out["long_round_cost"] = ((a2i > 365).to_numpy() & rnd).astype("float64")
    if "mupx" in g:
        mup = (out["related_mup_flag"] == 1).to_numpy()
        out["mup_sp_missing"] = (mup & sp_miss).astype("float64")
        out["mup_no_units"] = (mup & ~(hua.to_numpy() > 0)).astype("float64")
        out["long_sp_missing"] = ((a2i > 365).to_numpy() & sp_miss).astype("float64")
    if "link" in g:
        out["link_count"] = out["dependentbuilding"] + out["parent_permit_flag"] + out["related_mup_flag"]
    if "spx" in g:
        out["a2i_sp_missing"] = a2i.where(sp_miss)
        out["a2i_new"] = a2i.where(is_new)
    for c in state["cats"]:
        if c == "originalzip" and cfg["zip"] != "cat":
            if cfg["zip"] == "freq":
                out[c] = X[c].astype("object").map(state["zipfreq"]).astype("float64").to_numpy()
            if cfg["zip"] == "te":
                te = state.get("zip_te_oof")
                if te is not None and len(te) == len(X):
                    out["zip_te"] = te  # out-of-fold values, training rows only (set transiently inside fit)
                else:
                    out["zip_te"] = X[c].astype("object").map(state["zip_te"]).fillna(state["zip_prior"]).astype("float64").to_numpy()
            continue
        out[c] = pd.Categorical(X[c].astype("object"), categories=state["levels"][c])
    if "combo" in g:
        out["combo"] = pd.Categorical(_combo(X), categories=state["levels"]["combo"])
    drop = [c for c in cfg["drop"] if c in out]
    return out.drop(columns=drop)


def fit(X_train, y_train, *, seed, threads):
    cfg = dict(CFG)
    cats = [c for c in CATS if c in X_train]
    num = [c for c in X_train if c not in cats]
    levels = {}
    for c in cats:
        vc = X_train[c].dropna().value_counts()
        levels[c] = pd.Index(sorted(vc[vc >= cfg["min_level"]].index))  # rare levels -> missing
    vc = _combo(X_train).value_counts()
    levels["combo"] = pd.Index(sorted(vc[vc >= cfg["min_level"]].index))
    state = {"cfg": cfg, "cats": cats, "num": num, "levels": levels,
             "zipfreq": X_train["originalzip"].astype("object").value_counts(normalize=True).to_dict()}
    if cfg["zip"] == "te":
        m_s = float(cfg.get("te_m", 100))
        z = X_train["originalzip"].astype("object").fillna("NA").to_numpy()
        yv = np.asarray(y_train, dtype=float)
        fold = np.random.RandomState(seed).permutation(len(z)) % 5
        oof = np.zeros(len(z))
        for k in range(5):
            a = fold != k
            prior = yv[a].mean()
            g = pd.DataFrame({"z": z[a], "y": yv[a]}).groupby("z")["y"].agg(["sum", "count"])
            enc = (g["sum"] + m_s * prior) / (g["count"] + m_s)
            oof[~a] = pd.Series(z[~a]).map(enc).fillna(prior).to_numpy()
        prior = yv.mean()
        g = pd.DataFrame({"z": z, "y": yv}).groupby("z")["y"].agg(["sum", "count"])
        state["zip_te"] = ((g["sum"] + m_s * prior) / (g["count"] + m_s)).to_dict()
        state["zip_prior"] = float(prior)
        state["zip_te_oof"] = oof
    Z = prepare(state, X_train)
    state.pop("zip_te_oof", None)
    extra = {}
    if cfg["mono"]:
        extra["monotone_constraints"] = {c: s for c, s in dict(MONO, **cfg["mono_extra"]).items() if c in Z}
    if cfg["additive"]:
        add = [c for c in cfg["additive"] if c in Z]
        extra["interaction_constraints"] = [[c for c in Z.columns if c not in add]] + [[c] for c in add]
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, max_cat_to_onehot=cfg["onehot"],
                          random_state=seed, n_jobs=threads, **extra, **PARAMS)
    m.fit(Z, y_train)
    state["model"] = m
    return state


def prepare(state, X):
    return _features(state, X)
