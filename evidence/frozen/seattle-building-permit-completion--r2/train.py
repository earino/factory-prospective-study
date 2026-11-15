"""Self-contained XGBoost solution. Change this file; use evaluate.py to test.

One shallow XGBClassifier on the released row-local predictors plus label-free
engineered columns. All learned state (category levels, group medians, cell
codes, column order, model) is returned by fit; prepare uses that state only and
works on one row at a time. The experimental toggles screened during the search
are kept in diag/train_experimental.py; this file is the selected configuration.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {
    "n_estimators": 600, "max_depth": 2, "learning_rate": 0.03,
    # bagged trees per boosting round inside the single classifier (variance reduction)
    "num_parallel_tree": 8, "subsample": 0.6, "colsample_bynode": 0.6,
    "max_cat_to_onehot": 64,
}
CATS = ["permitclass", "permitclassmapped", "permittypedesc", "originalzip"]
# Plan-review columns are recorded for only ~14% of training rows (2018Q2 onward) and review days is
# nearly collinear with applied_to_issued_days; only their blank indicators are kept.
REVIEW = ["totaldaysplanreview", "numberreviewcycles", "daysoutcorrections"]
MIN_GROUP = 30
# Extra training weight for rows whose plan-review days are recorded (the recording regime that starts
# in 2018Q2 and covers ~70% of later permits). A feature-based proxy for recency; row order is not used.
RECORDED_WEIGHT = 0.5


def _num(X, c):
    return pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float)


def _text(X, c):
    return X[c].astype(object).astype(str)


def _group_key(X):
    return (_text(X, "permitclass") + "|" + _text(X, "permittypedesc")).to_numpy()


def _cell_key(X):
    hu_blank = np.isnan(_num(X, "housingunitsadded")).astype(int).astype(str)
    sp_blank = np.isnan(_num(X, "standardplan")).astype(int).astype(str)
    return (_text(X, "permitclass") + "|" + _text(X, "permittypedesc") + "|" + hu_blank + "|" + sp_blank).to_numpy()


def _features(X, stats):
    out = {}
    td = _num(X, "totaldaysplanreview")
    nrc = _num(X, "numberreviewcycles")
    a2i = _num(X, "applied_to_issued_days")
    cost = _num(X, "estprojectcost")
    hua = _num(X, "housingunitsadded")
    sp = _num(X, "standardplan")

    # A truly blank review-cycle counter is kept as a flag (distinct from the 0 = "not recorded" of pre-2018Q2 rows).
    out["nrc_blank"] = np.isnan(nrc).astype(float)

    for c in X.columns:
        if c not in CATS and c not in REVIEW:
            out[c] = _num(X, c)
    # Training rows only contain 0/blank; a later value of 1 must not fall on an untrained branch.
    out["standardplan"] = np.where(np.isnan(sp), np.nan, 0.0)

    # Blank-pattern indicators.
    hu_blank = np.isnan(hua).astype(float)
    sp_blank = np.isnan(sp).astype(float)
    td_blank = np.isnan(td).astype(float)
    out["huna"] = hu_blank
    out["spna"] = sp_blank
    out["tdna"] = td_blank
    out["miss_pattern"] = hu_blank + 2 * sp_blank + 4 * td_blank
    out["hu_no_sp"] = ((hu_blank == 0) & (sp_blank == 1)).astype(float)
    # Delay and declared cost relative to the training median of the same class x type (label-free).
    key = _group_key(X)
    med_a = np.array([stats["a2i"].get(k, stats["a2i_all"]) for k in key], dtype=float)
    med_c = np.array([stats["cost"].get(k, stats["cost_all"]) for k in key], dtype=float)
    out["a2i_rel"] = a2i - med_a
    out["a2i_ratio"] = (a2i + 7.0) / (med_a + 7.0)
    out["cost_ratio"] = np.log10(np.maximum(cost, 1.0)) - np.log10(np.maximum(med_c, 1.0))

    # Frequency rank of the class x type x blank-pattern cell (label-free); unseen or rare cells -> NaN.
    out["cell"] = np.array([stats["cells"].get(k, np.nan) for k in _cell_key(X)], dtype=float)
    return out


def prepare(state, X):
    df = pd.DataFrame(_features(X, state["stats"]), index=X.index)
    for c, levels in state["levels"].items():
        df[c] = pd.Categorical(X[c].astype(object), categories=levels)
    return df[state["cols"]]


def fit(X_train, y_train, *, seed, threads):
    X_train = X_train.copy()
    y = np.asarray(y_train)
    levels = {c: pd.Index(sorted(X_train[c].dropna().astype(object).unique(), key=str)) for c in CATS}

    gk = pd.Series(_group_key(X_train), index=X_train.index)
    a = pd.to_numeric(X_train["applied_to_issued_days"], errors="coerce")
    c = pd.to_numeric(X_train["estprojectcost"], errors="coerce")
    big = gk.map(gk.value_counts()) >= MIN_GROUP
    ck = pd.Series(_cell_key(X_train), index=X_train.index)
    vc = ck.value_counts()
    vc = vc[vc >= MIN_GROUP]
    stats = {
        "a2i": a[big].groupby(gk[big]).median().to_dict(), "a2i_all": float(a.median()),
        "cost": c[big].groupby(gk[big]).median().to_dict(), "cost_all": float(c.median()),
        "cells": {k: float(i) for i, k in enumerate(sorted(vc.index, key=lambda k: (-vc[k], k)))},
    }

    state = {"stats": stats, "levels": levels}
    state["cols"] = list(_features(X_train.iloc[:5], stats).keys()) + list(levels.keys())
    model = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, random_state=seed, n_jobs=threads, **PARAMS)
    weight = 1.0 + RECORDED_WEIGHT * X_train["totaldaysplanreview"].notna().to_numpy(dtype=float)
    model.fit(prepare(state, X_train), y, sample_weight=weight)
    state["model"] = model
    return state
