import os
"""Probe selected training features on full actual training data; no tree fitting or scores."""
import importlib.util,json
from pathlib import Path
import numpy as np,pandas as pd,xgboost as xgb
ROOT=Path(os.environ['STUDY_ROOT']);OUT=Path(os.environ['REVIEW_OUT']); OUT.mkdir(parents=True,exist_ok=True)
def allowed(rid):
 q=json.loads((ROOT/'.study/runs'/rid/'release/reproduction/construction.json').read_text())['quality']
 blocked=set(q.get('id_columns',[])+q.get('carry_columns',[])+q.get('post_hoc_columns',[])+q.get('label_source_columns',[])+[q['target']])
 return [c for c in q['features'] if c not in blocked]

class Spy:
 def __init__(self,**kw):self.kw=kw
 def set_params(self,**kw):self.kw.update(kw);return self
 def fit(self,X,y,**kw):self.matrix=X.copy();return self
xgb.XGBClassifier=Spy

def values(z):
 if isinstance(z,pd.DataFrame):
  z=z.copy()
  for c in z:
   if isinstance(z[c].dtype,pd.CategoricalDtype):z[c]=z[c].cat.codes
 return np.asarray(z,dtype=float)
report_path=OUT/"training-feature-probes.json"
reports=json.loads(report_path.read_text()) if report_path.exists() else []
for rid in json.loads((ROOT/'study.json').read_text())['order']:
 if any(r.get('run')==rid and 'error' not in r for r in reports):continue
 reports=[r for r in reports if r.get('run')!=rid]
 spec=importlib.util.spec_from_file_location('review_solution',ROOT/'evidence/frozen'/rid/'train.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 rel=ROOT/'.study/runs'/rid/'release/extract';meta=json.loads((rel/'meta.json').read_text());df=pd.read_csv(rel/'public/train.csv');y=(df[meta['target']]==meta.get('positive_label',1)).astype(int).to_numpy();X=df[allowed(rid)]
 try:
  a=m.fit(X,y,seed=42,threads=5);A=values(a['model'].matrix);assert len(A)%len(y)==0
  rowchecks=[]
  for idx in sorted({0,len(y)//2}):
   y2=y.copy();y2[idx]=1-y2[idx];b=m.fit(X,y2,seed=42,threads=5);B=values(b['model'].matrix);copyrows=np.arange(idx,len(A),len(y));v=A[copyrows];w=B[copyrows];diff=~np.isclose(v,w,rtol=0,atol=1e-10,equal_nan=True)
   delta=np.abs(v-w);delta[np.isnan(delta)]=0
   rowchecks.append({'row':idx,'changed_own_feature_cells':int(diff.sum()),'max_absolute_change':float(np.max(delta)),'augmented_copies':len(copyrows)})
  reports.append({'run':rid,'full_training_rows':len(y),'training_feature_rows':len(A),'checks':rowchecks})
 except Exception as e:reports.append({'run':rid,'error':repr(e)})
 (OUT/'training-feature-probes.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(reports[-1]),flush=True)
