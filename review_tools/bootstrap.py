"""Paired entity bootstrap for frozen predictions; no fitting or model calls."""
import os,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
S=Path(os.environ['STUDY_ROOT']);O=Path(os.environ['REVIEW_OUT']);O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def auc_setup(y,p):
 order=np.argsort(p,kind='stable');starts=np.r_[0,1+np.flatnonzero(np.diff(p[order]))];return order,starts,y[order].astype(float)
def weighted_auc(setup,w):
 order,starts,y=setup;z=w[order];pos=np.add.reduceat(z*y,starts);neg=np.add.reduceat(z*(1-y),starts);a=pos.sum();b=neg.sum()
 return np.sum(pos*(np.cumsum(neg)-.5*neg))/(a*b) if a and b else np.nan
protocol=json.loads((S/'study.json').read_text());ds=protocol['datasets'][0]
cluster=Path(os.environ['CLUSTER_FILE']);decl=json.loads(cluster.read_text())
if decl.get('status')!='declared' or not decl.get('cluster_columns'):raise ValueError('Prescoring dependence structure unresolved')
hp=S/'.study/holdout'/ds/'holdout.csv';df=pd.read_csv(hp);keys=decl['cluster_columns']
if any(k not in df for k in keys):raise ValueError('Prescoring cluster columns missing')
m=json.loads((S/'.study/releases'/ds/'extract/meta.json').read_text());y=(df[m['target']]==m.get('positive_label',1)).to_numpy().astype(int)
labels=pd.MultiIndex.from_frame(df[keys].astype('string').fillna('__MISSING_CLUSTER__'));g,lv=pd.factorize(labels,sort=True);G=len(lv)
ids=[ds+'--ordinary']+[ds+f'--r{i}' for i in range(1,4)]+[ds+f'--r{i}--random' for i in range(1,4)]
setup={};inputs={str(hp):sha(hp),str(cluster):sha(cluster)}
for rid in ids:
 path=S/'results/scores'/rid/'predictions.csv.gz'
 if not path.exists():continue
 p=pd.read_csv(path);assert np.array_equal(p.row,np.arange(len(y)));setup[rid]=auc_setup(y,p.p.to_numpy());inputs[str(path)]=sha(path)
seed=int(hashlib.sha256(ds.encode()).hexdigest()[:8],16);rng=np.random.default_rng(seed);draws=[];invalid=0
for _ in range(2000):
 w=np.bincount(rng.integers(G,size=G),minlength=G)[g];a=[weighted_auc(v,w) for v in setup.values()]
 if not np.isfinite(a).all():invalid+=1;continue
 draws.append(a)
a=np.asarray(draws);names=list(setup);comparisons=[]
for i in range(1,4):
 rid=ds+f'--r{i}'
 for control in [ds+'--ordinary',rid+'--random']:
  if rid not in setup or control not in setup or len(a)==0:continue
  delta=a[:,names.index(rid)]-a[:,names.index(control)];lo,hi=np.quantile(delta,[.025,.975]);w=np.ones(len(y));comparisons.append(dict(run=rid,control=control,delta=float(weighted_auc(setup[rid],w)-weighted_auc(setup[control],w)),low=float(lo),high=float(hi)))
r=dict(dataset=ds,cluster_columns=keys,clusters=G,rows=len(y),positives=int(y.sum()),missing_cluster_rows=int(df[keys].isna().any(axis=1).sum()),largest_cluster=int(np.bincount(g).max()),seed=seed,valid_replicates=len(a),invalid_replicates=invalid,comparisons=comparisons,inputs=inputs,method='2000 paired whole-entity draws, pointwise percentile95%; conditional on fitted models, cohort and declared dependence')
(O/'bootstrap.json').write_text(json.dumps(r,indent=2)+'\n');np.savez_compressed(O/'bootstrap-draws.npz',auc=a,ids=names)
print(json.dumps(r))
