"""Self-contained XGBoost solution. Change this file; use evaluate.py to test."""
import numpy as np
import pandas as pd
import xgboost as xgb
PARAMS = {"n_estimators": 100, "max_depth": 6, "learning_rate": 0.1}

def fit(X_train, y_train, *, seed, threads):
    cats = [c for c in X_train if pd.api.types.is_object_dtype(X_train[c]) or pd.api.types.is_string_dtype(X_train[c])]
    cats = [c for c in cats if X_train[c].nunique() <= 1000]
    cols = [c for c in X_train if not (pd.api.types.is_object_dtype(X_train[c]) or pd.api.types.is_string_dtype(X_train[c])) or c in cats]
    levels = {c: pd.Index(sorted(X_train[c].dropna().unique())) for c in cats}
    state = {"cols": cols, "levels": levels}
    m = xgb.XGBClassifier(tree_method="hist", enable_categorical=True, random_state=seed, n_jobs=threads, **PARAMS)
    m.fit(prepare(state, X_train), y_train)
    state["model"] = m
    return state

def prepare(state, X):
    out = X[state["cols"]].copy()
    for c, lv in state["levels"].items():
        out[c] = pd.Categorical(out[c], categories=lv)
    return out

def predict(model, X):
    return model["model"].predict_proba(prepare(model, X))[:, 1]
