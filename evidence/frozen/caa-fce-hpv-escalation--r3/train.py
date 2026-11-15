"""Self-contained XGBoost solution (single XGBClassifier; all preprocessing state fitted on training rows only)."""
import numpy as np, pandas as pd, xgboost as xgb
CATS=["state","epa_region","sic_2digit","naics_2digit","facility_type_code","air_pollutant_class_code","comp_monitor_type_code","state_epa_flag"]
NUMS=["program_count","pollutant_count","prior_evaluations_3y","days_since_last_evaluation","prior_stack_test_failures_3y","prior_hpv_count","days_since_hpv_resolution","prior_formal_actions_3y","prior_penalties_3y","prior_tv_deviations_3y"]
DEF={'cap': {'days_since_hpv_resolution': 3650, 'days_since_last_evaluation': 1825},
 'cat_mode': 'mixed',
 'drop': ['comp_monitor_type_code'],
 'eng': True,
 'freq': [],
 'native_cols': ['state', 'facility_type_code', 'air_pollutant_class_code', 'comp_monitor_type_code',
                 'state_epa_flag'],
 'ordinal_cols': ['epa_region', 'sic_2digit', 'naics_2digit'],
 'params': {'colsample_bytree': 0.5,
            'gamma': 0.5,
            'learning_rate': 0.03,
            'max_depth': 4,
            'min_child_weight': 10,
            'n_estimators': 130},
 'te': [['state', 'air_pollutant_class_code'], ['naics_2digit', 'air_pollutant_class_code']],
 'te_fold': 'mod',
 'te_hier': True,
 'te_k': 10,
 'te_m': 400.0}
def _key(v):
    # canonical string key for a categorical value, robust to int/float/str dtype differences
    if v is None: return "__NA__"
    if isinstance(v,(float,np.floating)):
        if np.isnan(v): return "__NA__"
        if float(v).is_integer(): return str(int(v))
        return str(v)
    if isinstance(v,(int,np.integer)): return str(int(v))
    s=str(v).strip()
    try:
        f=float(s)
        if np.isnan(f): return "__NA__"
        if f.is_integer(): return str(int(f))
    except ValueError: pass
    return s
def _keys(X,c):
    if c.startswith("@"):  # derived 0/1 or small-integer history flags (no labels involved)
        f=lambda k: pd.to_numeric(X[k],errors="coerce").to_numpy(dtype=np.float64)
        if c=="@hpv": v=(f("prior_hpv_count")>0)*1+(f("days_since_hpv_resolution")<=1825)*1
        elif c=="@st": v=(f("prior_stack_test_failures_3y")>0)*1
        elif c=="@fa": v=(f("prior_formal_actions_3y")>0)*1
        elif c=="@tv": v=(f("prior_tv_deviations_3y")>0)*1
        elif c=="@bad": v=np.minimum((f("prior_stack_test_failures_3y")>0)*1+(f("prior_formal_actions_3y")>0)*1+(f("prior_tv_deviations_3y")>0)*1,2)
        elif c=="@prog": v=np.minimum(f("program_count"),5)
        return [str(int(a)) for a in v]
    return [_key(v) for v in X[c].tolist()]
def _combo(X,cs):
    ks=[_keys(X,c) for c in cs]
    return ["|".join(t) for t in zip(*ks)]
def _te_fit(keys,y,m,prior):
    df=pd.DataFrame({"k":keys,"y":y}).groupby("k")["y"].agg(["sum","count"])
    return {k:(s+prior*m)/(n+m) for k,s,n in zip(df.index,df["sum"],df["count"])}
def _indic(X):
    N={k:pd.to_numeric(X[k],errors="coerce").to_numpy(dtype=np.float64) for k in NUMS}
    dh=N["days_since_hpv_resolution"];hpv=N["prior_hpv_count"]
    with np.errstate(all="ignore"):
        return {"hpv_any":(hpv>0)*1.0,"hpv_1y":(dh<=365)*1.0,"hpv_3y":(dh<=1095)*1.0,"hpv_5y":(dh<=1825)*1.0,"hpv_cnt":np.minimum(hpv,10),
            "fa_any":(N["prior_formal_actions_3y"]>0)*1.0,"st_any":(N["prior_stack_test_failures_3y"]>0)*1.0,"tv_any":(N["prior_tv_deviations_3y"]>0)*1.0,
            "ev_cnt":np.minimum(N["prior_evaluations_3y"],20),"pen_any":(N["prior_penalties_3y"]>0)*1.0}
def fit(X,y,*,seed,threads,cfg=None):
    c=dict(DEF);c.update(cfg or {})
    y=np.asarray(y);n=len(y);prior=float(y.mean())
    state={"cfg":c,"prior":prior}
    state["levels"]={k:{v:i for i,v in enumerate(sorted(set(_keys(X,k))-{"__NA__"}))} for k in CATS}
    state["freq"]={}
    for cs in c["freq"]:
        ks=_combo(X,cs);vc=pd.Series(ks).value_counts()
        state["freq"]["|".join(cs)]={k:v/n for k,v in vc.items()}
    # target encodings: full-train map for scoring, out-of-fold values for training rows
    state["te"]={};state["te_parent"]={};oof={}
    rng=np.random.RandomState(seed);fold=rng.randint(0,c["te_k"],n)
    if c.get("te_fold")=="mod": fold=np.arange(n)%c["te_k"]   # seed-independent, evenly interleaved folds
    for cs in c["te"]:
        name="|".join(cs);ks=np.array(_combo(X,cs),dtype=object)
        hier=bool(c.get("te_hier")) and len(cs)>1
        pk=np.array(_combo(X,cs[1:]),dtype=object) if hier else None   # parent = combo without its first column
        def enc(tr,pr,ks_out,pk_out):
            if not hier:
                mp=_te_fit(ks[tr],y[tr],c["te_m"],pr);return [mp.get(k,pr) for k in ks_out],mp,None
            pm=_te_fit(pk[tr],y[tr],c.get("te_pm",50.0),pr)
            df=pd.DataFrame({"k":ks[tr],"p":pk[tr],"y":y[tr]}).groupby("k").agg(s=("y","sum"),n=("y","count"),p=("p","first"))
            mp={k:(a+pm[q]*c["te_m"])/(b+c["te_m"]) for k,a,b,q in zip(df.index,df["s"],df["n"],df["p"])}
            return [mp[k] if k in mp else pm.get(q,pr) for k,q in zip(ks_out,pk_out)],mp,pm
        allr=np.ones(n,dtype=bool)
        _,mp,pm=enc(allr,prior,[],[])
        state["te"][name]=mp;state["te_parent"][name]=pm
        o=np.empty(n)
        for f in range(c["te_k"]):
            tr=fold!=f;pr=float(y[tr].mean())   # prior and parent rates exclude held-out fold labels
            o[~tr]=enc(tr,pr,ks[~tr],pk[~tr] if hier else ks[~tr])[0]
        oof[name]=o
    state["gs"]={}
    if c.get("gstats"):
        I=_indic(X)
        for cs,ind in c["gstats"]:
            ks=_combo(X,cs);g=float(np.mean(I[ind]));m=c.get("gs_m",20.0)
            df=pd.DataFrame({"k":ks,"v":I[ind]}).groupby("k")["v"].agg(["sum","count"])
            state["gs"]["|".join(cs)+"@"+ind]=({k:(a+g*m)/(b+m) for k,a,b in zip(df.index,df["sum"],df["count"])},g)
    Z=prepare(state,X)
    names=state["names"]
    for name,o in oof.items(): Z[:,names.index("te_"+name)]=o
    ft=state["ftypes"]
    kw=dict(tree_method="hist",random_state=seed,n_jobs=threads)
    if "c" in ft: kw.update(enable_categorical=True,feature_types=ft)
    kw.update(c["params"])
    if c.get("additive"):  # listed features may not interact with any other feature
        solo=[names.index(a) for a in c["additive"] if a in names]
        kw["interaction_constraints"]=str([[i] for i in solo]+[[i for i in range(len(names)) if i not in solo]])
    if c.get("mono"): kw["monotone_constraints"]=tuple(int(c["mono"].get(nm,0)) for nm in names)
    sw=None
    if c.get("decay"): # recency weights by row order (training file is chronological)
        sw=np.exp(-c["decay"]*(1-np.arange(n)/max(1,n-1)))
    m=xgb.XGBClassifier(**kw);m.fit(Z,y,sample_weight=sw)
    state["model"]=m
    return state
def prepare(state,X):
    c=state["cfg"];cols=[];names=[];ft=[]
    def add(nm,v,t="q"):
        if nm in c["drop"]: return
        cols.append(np.asarray(v,dtype=np.float64));names.append(nm);ft.append(t)
    if c["cat_mode"] in ("native","ordinal"):
        for k in CATS:
            lv=state["levels"][k];add(k,[lv.get(v,np.nan) for v in _keys(X,k)],"c" if c["cat_mode"]=="native" else "q")
    elif c["cat_mode"]=="mixed":  # native for low-card, none for others (TE/freq cover them)
        for k in c["native_cols"]:
            lv=state["levels"][k];add(k,[lv.get(v,np.nan) for v in _keys(X,k)],"c")
        for k in c.get("ordinal_cols",[]):
            lv=state["levels"][k];add(k,[lv.get(v,np.nan) for v in _keys(X,k)],"q")
    N={k:pd.to_numeric(X[k],errors="coerce").to_numpy(dtype=np.float64) for k in NUMS}
    for k,v in (c.get("cap") or {}).items(): N[k]=np.minimum(N[k],v)   # NaN stays NaN
    for k in NUMS: add(k,N[k])
    for name,mp in state["freq"].items():
        add("fr_"+name,[mp.get(k,0.0) for k in _combo(X,name.split("|"))])
    for name,mp in state["te"].items():
        cs=name.split("|");pm=state.get("te_parent",{}).get(name)
        if pm is None: add("te_"+name,[mp.get(k,state["prior"]) for k in _combo(X,cs)])
        else: add("te_"+name,[mp[k] if k in mp else pm.get(q,state["prior"]) for k,q in zip(_combo(X,cs),_combo(X,cs[1:]))])
    for name,(mp,g) in state.get("gs",{}).items():
        add("gs_"+name,[mp.get(k,g) for k in _combo(X,name.split("@")[0].split("|"))])
    if c["eng"]:
        hpv=N["prior_hpv_count"];fa=N["prior_formal_actions_3y"];st=N["prior_stack_test_failures_3y"];tv=N["prior_tv_deviations_3y"]
        ev=N["prior_evaluations_3y"];pen=N["prior_penalties_3y"];dh=N["days_since_hpv_resolution"];de=N["days_since_last_evaluation"]
        pc=N["program_count"];pl=N["pollutant_count"]
        with np.errstate(all="ignore"):
            add("pen_per_action",np.where(fa>0,pen/np.maximum(fa,1),np.nan))
            add("bad_sum",fa+st+tv)
            add("bad_any",(fa>0).astype(float)+(st>0)+(tv>0)+(hpv>0))
            add("hpv_rate",hpv/(1.0+np.nan_to_num(dh,nan=20000.)/365.))
            add("hpv_recent",hpv*np.exp(-np.nan_to_num(dh,nan=1e9)/1095.))
            add("fa_per_eval",fa/(1.0+ev))
            add("tv_per_eval",tv/(1.0+ev))
            add("poll_per_prog",pl/np.maximum(pc,1))
            add("hpv_no_res",((hpv>0)&np.isnan(dh)).astype(float))
            add("dh_minus_de",dh-de)
    state["names"]=names;state["ftypes"]=ft
    return np.column_stack(cols).astype(np.float32)
