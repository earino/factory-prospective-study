"""Self-contained XGBoost solution for fda-510k-five-year-recall (simplified final version).

Features (all from the nine declared predictors; no date, no identifier):
  * raw numerics and low-cardinality native categoricals;
  * te_product_code   smoothed target rate of the product code (out-of-fold over chronological blocks in fit);
  * freq_product_code label-free training share of the product code;
  * wr_/wn_           "pseudo-firm history": applicant_prior_clearances rises along an applicant's trajectory,
                      so for a row with count c we take the smoothed label rate (and number) of training rows
                      sharing a key whose count lies in [c - ceil(w0 + a*c), c - 1] (count 0 -> count-0 rows).
                      In fit these use strictly earlier chronological blocks only.
fit() relies on X_train arriving in chronological row order (block construction only); prepare() uses one row
plus fitted state and is independent of row order and batch size.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

CATS = ["advisory_committee", "device_class", "clearance_type", "third_party_flag", "applicant_country_code"]
NUMS = ["review_days", "applicant_prior_clearances"]
TE_COL = "product_code"
COUNT = "applicant_prior_clearances"
# (key columns, w0, a) for the windowed pseudo-firm history
WINDOWS = [(("applicant_country_code", "product_code"), 2, 0.5),
           (("applicant_country_code", "advisory_committee"), 2, 0.25)]
TE_M = 20.0     # smoothing pseudo-count of the product-code encoding
W_M = 10.0      # smoothing pseudo-count of the window rates
FOLDS = 10      # contiguous chronological blocks for the pseudo-firm windows
TE_FOLDS = 3    # coarser blocks for the product encoding: training rows are encoded from labels far in time,
                # as prediction rows are (finer blocks let near-in-time sibling recalls inflate the encoding)
PARAMS = {"n_estimators": 400, "max_depth": 3, "learning_rate": 0.03, "min_child_weight": 5, "subsample": 0.8,
          "colsample_bytree": 0.8, "reg_lambda": 5.0, "max_cat_to_onehot": 64, "max_cat_threshold": 16}


def _canon(v):
    """Canonical string for a raw cell so that '2', 2 and 2.0 agree whatever dtype the CSV reader inferred."""
    if v is None or (isinstance(v, float) and v != v):
        return "nan"
    if isinstance(v, (int, np.integer)) and not isinstance(v, (bool, np.bool_)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        return str(int(v)) if float(v).is_integer() else str(float(v))
    t = str(v).strip()
    if t.endswith(".0") and t[:-2].lstrip("-").isdigit():
        t = t[:-2]
    return t


def _col(X, c):
    return pd.Series([_canon(v) for v in X[c].tolist()], index=X.index, dtype=object)


def _key(X, cols):
    s = _col(X, cols[0])
    for c in cols[1:]:
        s = s + "|" + _col(X, c)
    return s.to_numpy()


def _wname(spec):
    return "+".join(spec[0]) + "_%g_%g" % (spec[1], spec[2])


def _te_table(key, y, m, prior):
    g = pd.DataFrame({"k": key, "y": y}).groupby("k")["y"].agg(["sum", "count"])
    return {kk: (float(a) + m * prior) / (float(b) + m) for kk, a, b in zip(g.index, g["sum"], g["count"])}


def _wbuild(keys, cnt, y):
    """key -> (sorted counts, prefix sums of labels in that order)."""
    df = pd.DataFrame({"k": np.asarray(keys), "c": np.asarray(cnt, dtype=float), "y": np.asarray(y, dtype=float)})
    df = df[np.isfinite(df["c"])].sort_values(["k", "c"], kind="mergesort")
    return {kk: (g["c"].to_numpy(), np.concatenate([[0.0], np.cumsum(g["y"].to_numpy())]))
            for kk, g in df.groupby("k", sort=False)}


def _wquery(d, keys, cnt, w0, a, m, prior):
    rate = np.empty(len(keys))
    num = np.empty(len(keys))
    for i, (kk, c) in enumerate(zip(keys, cnt)):
        t = d.get(kk)
        n = s = 0.0
        if t is not None and c == c:
            if c <= 0:
                lo = hi = 0.0
            else:
                lo = c - np.ceil(w0 + a * c)
                hi = c - 1.0
            i0 = np.searchsorted(t[0], lo, "left")
            i1 = np.searchsorted(t[0], hi, "right")
            n = float(i1 - i0)
            s = float(t[1][i1] - t[1][i0])
        rate[i] = (s + m * prior) / (n + m)
        num[i] = n
    return rate, num


def fit(X_train, y_train, *, seed, threads):
    X = X_train.reset_index(drop=True)
    y = np.asarray(y_train, dtype=float)
    n = len(X)
    prior = float(y.mean())
    fold = (np.arange(n) * FOLDS // n).astype(int)  # rows arrive in chronological order
    cnt = pd.to_numeric(X[COUNT], errors="coerce").to_numpy(dtype=float)
    state = {"prior": prior,
             "levels": {c: pd.Index(sorted(set(_col(X, c)[X[c].notna().to_numpy()]))) for c in CATS}}
    oof = {}

    # product-code target encoding: full table for prediction, out-of-fold values for the training matrix
    key = _key(X, (TE_COL,))
    state["te"] = _te_table(key, y, TE_M, prior)
    enc = np.empty(n)
    tfold = (np.arange(n) * TE_FOLDS // n).astype(int)
    for f in range(TE_FOLDS):
        inm = tfold == f
        pf = float(y[~inm].mean())  # the prior also excludes the held-out block's labels
        tab = _te_table(key[~inm], y[~inm], TE_M, pf)
        enc[inm] = [tab.get(kk, pf) for kk in key[inm]]
    oof["te_" + TE_COL] = enc
    vc = pd.Series(key).value_counts()
    state["freq"] = {kk: float(v) / n for kk, v in zip(vc.index, vc.values)}

    # pseudo-firm windows: training rows only see strictly earlier blocks (block 0 has no history -> missing)
    state["win"] = {}
    for spec in WINDOWS:
        cols, w0, a = spec
        key = _key(X, cols)
        state["win"][_wname(spec)] = _wbuild(key, cnt, y)
        r = np.full(n, np.nan)
        c_ = np.full(n, np.nan)
        for f in range(1, FOLDS):
            inm = fold == f
            use = fold < f
            r[inm], c_[inm] = _wquery(_wbuild(key[use], cnt[use], y[use]), key[inm], cnt[inm], w0, a, W_M,
                                      float(y[use].mean()))
        oof["wr_" + _wname(spec)] = r
        oof["wn_" + _wname(spec)] = c_

    F = prepare(state, X)
    for name, v in oof.items():
        assert name in F.columns
        F[name] = v
    model = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, random_state=seed, n_jobs=threads,
                              monotone_constraints={"te_" + TE_COL: 1}, **PARAMS)
    model.fit(F, y_train)
    state["model"] = model
    return state


def prepare(state, X):
    out = {}
    for c in NUMS:
        out[c] = pd.to_numeric(X[c], errors="coerce").to_numpy(dtype=float)
    for c in CATS:
        out[c] = pd.Categorical(_col(X, c).where(X[c].notna().to_numpy()), categories=state["levels"][c])
    key = _key(X, (TE_COL,))
    out["te_" + TE_COL] = np.array([state["te"].get(kk, state["prior"]) for kk in key], dtype=float)
    out["freq_" + TE_COL] = np.array([state["freq"].get(kk, 0.0) for kk in key], dtype=float)
    cnt = out[COUNT]
    for spec in WINDOWS:
        nm = _wname(spec)
        r, c_ = _wquery(state["win"][nm], _key(X, spec[0]), cnt, spec[1], spec[2], W_M, state["prior"])
        out["wr_" + nm] = r
        out["wn_" + nm] = c_
    return pd.DataFrame(out)


def predict(model, X):
    return model["model"].predict_proba(prepare(model, X))[:, 1]
