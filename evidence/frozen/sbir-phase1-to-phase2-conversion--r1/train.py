"""H15: H13 with the upper reference amount taken at the 95th instead of the 90th percentile.

Model: f(number_employees) + g(agency, branch, program, ownership flags, award amount, relative award amount),
one XGBClassifier with interaction constraints, recency-weighted. No target-derived statistics.
"""
import numpy as np
import pandas as pd
import xgboost as xgb

CATS = ["agency", "branch", "program", "hubzone_owned", "women_owned", "socially_economically_disadvantaged"]
REL = ["rel_med", "rel_hi", "rel_spread"]   # amount / q20 ("rel_base") removed: most sensitive to stale references
PARAMS = dict(n_estimators=200, max_depth=3, learning_rate=0.02, subsample=0.7, colsample_bytree=1.0,
              min_child_weight=40, reg_lambda=20.0, gamma=1.0, max_bin=16,
              # employees enter additively; the other fields interact only with each other
              interaction_constraints=[CATS + ["award_amount"] + REL, ["number_employees"]])
MIN_LEVEL = 15        # categorical levels with fewer training rows are treated as missing
DECAY = 0.15          # sample weight exp(-DECAY * (last training year - award_year))
MIN_REF = 8           # minimum training awards needed for a reference window


def _group(agency, branch):
    return str(agency) + "|" + (branch if isinstance(branch, str) else "NA")


def _reference_table(X):
    """Label-free reference amounts: 20th/50th/95th percentile of training award amounts per (agency|branch, year)
    and per (agency, year), over award years [y-2, y-1] (fallback [y-3, y] when fewer than MIN_REF awards)."""
    df = pd.DataFrame({"g": [_group(a, b) for a, b in zip(X["agency"], X["branch"])],
                       "a": X["agency"].astype(str).to_numpy(),
                       "y": X["award_year"].astype(int).to_numpy(),
                       "amt": X["award_amount"].astype(float).to_numpy()}).dropna()
    table = {}
    for key in ("g", "a"):
        for k, d in df.groupby(key):
            ys, am = d["y"].to_numpy(), d["amt"].to_numpy()
            for y in range(int(df["y"].min()), int(df["y"].max()) + 2):
                sel = am[(ys >= y - 2) & (ys <= y - 1)]
                if len(sel) < MIN_REF:
                    sel = am[(ys >= y - 3) & (ys <= y)]
                if len(sel) >= MIN_REF:
                    table[(k, y)] = tuple(float(q) for q in np.quantile(sel, [0.2, 0.5, 0.95]))
    return table


def _reference(state, agency, branch, year):
    y = int(min(year, state["last_year"] + 1))      # later years reuse the latest window
    for k in (_group(agency, branch), str(agency)):
        if (k, y) in state["rel"]:
            return state["rel"][(k, y)]
    return (np.nan, np.nan, np.nan)


def fit(X_train, y_train, *, seed, threads):
    year = X_train["award_year"].to_numpy()
    levels = {}
    for c in CATS:
        counts = X_train[c].astype(object).where(X_train[c].notna(), "NA").value_counts()
        levels[c] = sorted(counts[counts >= MIN_LEVEL].index.tolist())
    state = {"levels": levels, "rel": _reference_table(X_train), "last_year": int(year.max())}
    model = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, max_cat_to_onehot=4,
                              random_state=seed, n_jobs=threads, **PARAMS)
    model.fit(prepare(state, X_train), y_train, sample_weight=np.exp(-DECAY * (year.max() - year)))
    state["model"] = model
    return state


def prepare(state, X):
    amount = X["award_amount"].astype(float).to_numpy()
    out = pd.DataFrame({"award_amount": amount,
                        "number_employees": X["number_employees"].astype(float).to_numpy()}, index=X.index)
    refs = np.array([_reference(state, a, b, y) for a, b, y in
                     zip(X["agency"].tolist(), X["branch"].tolist(), X["award_year"].tolist())], dtype=float).reshape(-1, 3)
    out["rel_med"] = amount / refs[:, 1]
    out["rel_hi"] = amount / refs[:, 2]
    out["rel_spread"] = refs[:, 2] / refs[:, 0]
    for c in CATS:
        out[c] = pd.Categorical(X[c].astype(object).where(X[c].notna(), "NA").to_numpy(), categories=state["levels"][c])
    return out
