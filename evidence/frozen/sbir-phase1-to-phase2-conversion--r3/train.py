"""Self-contained XGBoost solution for sbir-phase1-to-phase2-conversion.

One XGBClassifier on a small numeric feature set. Every feature is computed from one row's own permitted
predictor fields plus state fitted on the training partition only:

  agency, ag_branch   ordinal codes of levels seen in training (unseen -> NaN)
  program_sttr        1 if program == STTR
  award_year          federal fiscal year of the award (only if USE_YEAR)
  log_amt             log1p(award_amount)
  emp                 number_employees
  amt_per_emp         log1p(award_amount / (employees + 1))
  rel_amt, rel_base   log(award_amount / training median resp. 20th percentile of the amounts of the row's
                      agency|branch in its award_year). Years later than every fitted year of the group use the
                      group's latest fitted year. No labels enter these tables.

No target-derived encoding is used. Training rows get recency weights 0.5 ** ((max_year - year) / HALF_LIFE).
"""
import numpy as np
import pandas as pd
import xgboost as xgb

PARAMS = {"n_estimators": 300, "max_depth": 3, "learning_rate": 0.03, "subsample": 0.8,
          "colsample_bytree": 0.7, "min_child_weight": 5, "reg_lambda": 20.0}
HALF_LIFE = 6.0     # award-years; None disables recency weighting
REL_MIN_N = 8       # minimum training rows per (agency|branch, year) for an amount reference
REL_LAGS = (0, 1)   # as in the selected H8 model; the diag scripts override this
REL_KEY = "ag_branch"   # grouping of the amount references ("ag_branch" or "ag_branch_prog")
INFLATE = (0.95, 1.1)       # extra training copies with every amount multiplied by these factors (references unchanged)
INFLATE_SKIP = ()    # agencies whose rows get no inflated copy (their amount tiers carry real signal)
MAX_REF_AGE = None   # drop a reference that is more than this many years older than it needs to be
STRICT_LAGS = False  # lagged copies only for rows that really have a reference at least `lag` years old
USE_STATE_N = False  # label-free count of training firms in the row's state (ecosystem size)
DROP_FEATS = ()     # diagnostic only: feature columns removed from the matrix
POOL_STALE = False  # when the reference is stale, use the geometric mean of the two latest usable years
ADJ_COPIES = False  # also add copies whose absolute amount is rescaled into the group's latest fitted amount regime
USE_STALE = False   # add the age (years) of the reference actually used as a feature
USE_YEAR = False    # award_year as a model input was tested (trial 3317ff45) and gave no measurable gain


def _s(v):
    return v if isinstance(v, str) else None


def _num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return np.nan
    return v if v == v else np.nan


def _row(r):
    """Raw per-row values from the row's own fields."""
    ag = _s(r.get("agency")) or "?"
    br = _s(r.get("branch")) or "-"
    amt = _num(r.get("award_amount"))
    emp = _num(r.get("number_employees"))
    return {"agency": ag, "ag_branch": ag + "|" + br, "ag_branch_prog": ag + "|" + br + "|" + (_s(r.get("program")) or "?"),
            "state": _s(r.get("state")) or "?",
            "program_sttr": 1.0 if _s(r.get("program")) == "STTR" else 0.0,
            "award_year": _num(r.get("award_year")), "amt": amt,
            "log_amt": np.log1p(amt) if amt == amt else np.nan, "emp": emp,
            "amt_per_emp": np.log1p(amt / (emp + 1.0)) if amt == amt and emp == emp else np.nan}


def _raw(X):
    return pd.DataFrame([_row(r) for r in X.to_dict("records")])


def _ref_year(tab, yr, lag):
    """Year of the reference used for a row of award year yr: the latest fitted year <= yr - lag, else the earliest."""
    if not tab or yr != yr:
        return None
    want = int(yr) - lag
    earlier = [k for k in tab if k <= want]
    return max(earlier) if earlier else min(tab)


def _rel(tab, amt, yr, lag=0, gmax=None, max_age=None):
    """log(amount / reference amount); the reference year is chosen by _ref_year."""
    if not tab or amt != amt or amt <= 0 or yr != yr:
        return np.nan
    k = _ref_year(tab, yr, lag)
    if max_age is not None and gmax is not None and min(int(yr), gmax) - lag - k > max_age:
        return np.nan   # the group's usable reference is older than the newest one any group could have
    ref = tab[k]
    if POOL_STALE and k != int(yr):
        prev = [j for j in tab if j < k]
        if prev:
            ref = float(np.sqrt(ref * tab[max(prev)]))
    return float(np.log(amt / ref))


def _stale(tab, yr, lag=0):
    k = _ref_year(tab, yr, lag)
    return np.nan if k is None else float(int(yr) - k)


def _tables(R, q):
    """{agency|branch: {year: quantile q of training award amounts}} for groups with >= REL_MIN_N rows."""
    out = {}
    g = R.dropna(subset=["amt"]).groupby([REL_KEY, "award_year"])["amt"]
    val = g.median() if q is None else g.quantile(q)
    cnt = g.count()
    for (k, yy), v in val.items():
        if cnt[(k, yy)] >= REL_MIN_N and v > 0:
            out.setdefault(k, {})[int(yy)] = float(v)
    return out


def _adj_amt(tab, amt, yr):
    """amount * reference(latest fitted year) / reference(row year); unchanged without a table or for later years."""
    if not tab or amt != amt or yr != yr:
        return amt
    last = max(tab)
    if int(yr) >= last:
        return amt
    return amt * tab[last] / tab[_ref_year(tab, yr, 0)]


def _matrix(state, R, lag=0, adj=False):
    if adj:
        R = R.copy()
        a = np.array([_adj_amt(state["med"].get(g), x, y) for g, x, y in zip(R[state.get("rel_key", "ag_branch")], R["amt"], R["award_year"])], dtype=float)
        R["log_amt"] = np.log1p(a)
        R["amt_per_emp"] = np.log1p(a / (R["emp"].to_numpy(dtype=float) + 1.0))
    out = pd.DataFrame(index=R.index)
    out["agency"] = R["agency"].map(state["agency_code"]).astype(float)
    out["ag_branch"] = R["ag_branch"].map(state["branch_code"]).astype(float)
    for c in state["num_cols"]:
        out[c] = R[c].astype(float)
    out["rel_amt"] = [_rel(state["med"].get(g), a, y, lag, state.get("gmax"), state.get("max_age")) for g, a, y in zip(R[state.get("rel_key", "ag_branch")], R["amt"], R["award_year"])]
    out["rel_base"] = [_rel(state["p20"].get(g), a, y, lag, state.get("gmax"), state.get("max_age")) for g, a, y in zip(R[state.get("rel_key", "ag_branch")], R["amt"], R["award_year"])]
    if state.get("state_n") is not None:
        out["state_n"] = R["state"].map(state["state_n"]).astype(float).fillna(0.0)
    if state.get("use_stale"):
        out["stale"] = [_stale(state["med"].get(g), y, lag) for g, y in zip(R["ag_branch"], R["award_year"])]
    return out.astype(float).drop(columns=[c for c in DROP_FEATS if c in out.columns])


def fit(X_train, y_train, *, seed, threads):
    y = np.asarray(y_train).astype(int)
    R = _raw(X_train.reset_index(drop=True))
    num_cols = ["program_sttr"] + (["award_year"] if USE_YEAR else []) + ["log_amt", "emp", "amt_per_emp"]
    state = {"num_cols": num_cols,
             "agency_code": {k: i for i, k in enumerate(sorted(R["agency"].unique()))},
             "branch_code": {k: i for i, k in enumerate(sorted(R["ag_branch"].unique()))},
             "med": _tables(R, None), "p20": _tables(R, 0.2), "use_stale": bool(USE_STALE), "rel_key": REL_KEY, "max_age": MAX_REF_AGE,
             "gmax": int(np.nanmax(R["award_year"].to_numpy(dtype=float))),
             "state_n": np.log1p(R["state"].value_counts()).to_dict() if USE_STATE_N else None}
    yrs = R["award_year"].to_numpy(dtype=float)
    w = np.ones(len(R)) if not HALF_LIFE else 0.5 ** ((np.nanmax(yrs) - yrs) / float(HALF_LIFE))
    w = np.where(np.isfinite(w), w, 1.0)
    # one copy of the training rows per lag, each weighted 1/len(REL_LAGS); labels are the rows' own
    lags = tuple(REL_LAGS) if REL_LAGS else (0,)
    views = [(l, False) for l in lags] + ([(l, True) for l in lags] if ADJ_COPIES else [])
    mats, ys, ws = [], [], []
    for l, a in views:
        Ml = _matrix(state, R, lag=l, adj=a)
        keep = np.ones(len(R), dtype=bool)
        if STRICT_LAGS and l > 0:
            keep = np.array([bool(state["med"].get(g)) and y_ == y_ and min(state["med"][g]) <= int(y_) - l
                             for g, y_ in zip(R[REL_KEY], R["award_year"])])
        mats.append(Ml[keep]); ys.append(y[keep]); ws.append(w[keep] / len(views))
    nv = len(views) + len(INFLATE)
    ws = [x * len(views) / nv for x in ws]
    for fac in INFLATE:
        Rf = R.copy()
        Rf["amt"] = Rf["amt"] * fac
        Rf["log_amt"] = np.log1p(Rf["amt"])
        Rf["amt_per_emp"] = np.log1p(Rf["amt"] / (Rf["emp"] + 1.0))
        keepf = ~Rf["agency"].isin(list(INFLATE_SKIP)).to_numpy()
        mats.append(_matrix(state, Rf, lag=0)[keepf]); ys.append(y[keepf]); ws.append(w[keepf] / nv)
    M = pd.concat(mats, ignore_index=True)
    y = np.concatenate(ys)
    w = np.concatenate(ws)
    m = xgb.XGBClassifier(tree_method="hist", random_state=seed, n_jobs=threads, **PARAMS)
    m.fit(M, y, sample_weight=w)
    state["model"] = m
    return state


def prepare(state, X):
    return _matrix(state, _raw(X.reset_index(drop=True)))
