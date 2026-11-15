import numpy as np
import pandas as pd
import xgboost as xgb
PARAMS = {"n_estimators": 400, "max_depth": 3, "learning_rate": 0.03, "subsample": 0.6, "colsample_bynode": 0.3, "num_parallel_tree": 16, "min_child_weight": 5, "reg_lambda": 10.0}
CATS = ["permitclass", "permittypedesc", "originalzip"]
MINN = 30
FLAGS = {"combo", "newsp", "region"}
DROPF = ["doc", "description_length", "issue_month_sin", "issue_month_cos", "housingunitsremoved", "parent_permit_flag", "description_demolition", "otc", "hu_na", "rec", "cyc"]
MONO = None
WREC = 1.0   # sample-weight multiplier for rows with recorded plan review

REGIONS = {"central": ["98101", "98104", "98121", "98109", "98102", "98122", "98112"],
           "north": ["98103", "98105", "98107", "98115", "98117", "98125", "98133", "98177"],
           "south": ["98106", "98108", "98118", "98126", "98116", "98136", "98144", "98146", "98178", "98134"],
           "west": ["98119", "98199"]}

def _feats(X):
    f = pd.DataFrame(index=X.index)
    num = lambda c: pd.to_numeric(X[c], errors="coerce").astype(float)
    cost = num("estprojectcost"); f["logcost"] = np.log10(cost)
    for c in ["housingunitsadded", "housingunitsremoved", "housingunits", "applied_to_issued_days", "issue_month_sin", "issue_month_cos",
              "description_length", "description_stfi", "description_per_plan", "description_apartment", "description_unit",
              "description_tenant", "description_demolition", "dependentbuilding", "standardplan", "parent_permit_flag", "related_mup_flag"]:
        f[c] = num(c)
    tdpr = num("totaldaysplanreview"); cyc = num("numberreviewcycles"); doc = num("daysoutcorrections")
    f["cyc_na"] = cyc.isna().astype(float)
    rec = tdpr.notna() | (cyc > 0) | (doc > 0)
    cyc = cyc.where(rec); doc = doc.where(rec)
    f["tdpr"] = tdpr; f["cyc"] = cyc; f["doc"] = doc
    f["rec"] = rec.astype(float)
    f["city_days"] = tdpr - doc
    f["a2i_minus_tdpr"] = f["applied_to_issued_days"] - tdpr
    f["otc"] = (f["applied_to_issued_days"] <= 1).astype(float)
    f["hu_na"] = f["housingunitsadded"].isna().astype(float)
    f["cost_per_unit"] = np.log10(cost / f["housingunits"].clip(lower=1))
    f["cost_round"] = ((cost % 5000) == 0).astype(float)
    spna = f["standardplan"].isna(); hua = f["housingunitsadded"]
    typ = X["permittypedesc"].astype("string"); cls = X["permitclass"].astype("string")
    if "det" in FLAGS:
        f["sp_na_units"] = (spna & (hua > 0)).astype(float)
    if "state" in FLAGS:  # joint record-state code of standardplan / units-added missingness
        f["state"] = spna.astype(float) * 3 + np.where(hua.isna(), 2.0, np.where(hua > 0, 1.0, 0.0))
    if "newsp" in FLAGS:
        f["new_sp_na"] = (spna & (typ == "New").fillna(False)).astype(float)
    if "zipnum" in FLAGS:
        f["zipnum"] = pd.to_numeric(X["originalzip"], errors="coerce").astype(float)
    if "docratio" in FLAGS:
        f["doc_ratio"] = doc / tdpr.clip(lower=1)
        f["days_per_cycle"] = tdpr / cyc.clip(lower=1)
    if "a2ilog" in FLAGS:
        f["a2i_per_logcost"] = f["applied_to_issued_days"] / f["logcost"]
        f["desc_per_logcost"] = f["description_length"] / f["logcost"]
    if "region" in FLAGS:
        z = X["originalzip"].astype("string")
        for name, zs in REGIONS.items():
            f["region_" + name] = z.isin(zs).fillna(False).astype(float)
    if "units" in FLAGS:
        f["multi"] = (f["housingunits"] > 1).astype(float)
        f["unit_loss"] = (f["housingunits"] < 0).astype(float)
    if "combo" in FLAGS:
        for a in ["Commercial", "Single Family/Duplex", "Multifamily", "Institutional", "Industrial"]:
            for b in ["New", "Addition/Alteration"]:
                f[a + "|" + b] = ((cls == a) & (typ == b)).fillna(False).astype(float)
    return f

def fit(X_train, y_train, *, seed, threads):
    state = {"levels": {c: [v for v, n in X_train[c].astype("string").value_counts().items() if n >= MINN] for c in CATS}}
    Z = prepare(state, X_train)
    kw = {}
    if MONO: kw["monotone_constraints"] = {c: MONO.get(c, 0) for c in Z.columns}
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, **PARAMS, **kw)
    w = np.where(Z["rec"] > 0, WREC, 1.0) if (WREC != 1.0 and "rec" in Z) else None
    m.fit(Z, y_train, sample_weight=w)
    state["model"] = m
    return state

def prepare(state, X):
    f = _feats(X)
    for c, lv in state["levels"].items():
        s = X[c].astype("string")
        for v in lv:
            if c == "originalzip" and v not in ("missing", "other"): continue   # individual ZIPs pooled into regions
            f[c + "=" + v] = (s == v).fillna(False).astype(float).to_numpy()
    return f.drop(columns=[c for c in DROPF if c in f])
