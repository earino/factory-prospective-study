"""Resolve three old probe errors using inspected row mappings; no model fitting/scoring.

DataFrame indices identify retained rows. The FAA solution returns a NumPy matrix;
its inspected augmentation mapping is reconstructed from its frozen SIZE_MASK and
seed, and captured labels must agree with that mapping before probing.
Original frozen code and earlier reports are never modified.
"""
import importlib.util,json,hashlib,sys
from pathlib import Path
import numpy as np,pandas as pd,xgboost as xgb
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'paper/analysis/final-2026-11-16'
CASES=[('fda-510k-five-year-recall','fda-510k-five-year-recall--r2'),
       ('t100-new-route-survival','t100-new-route-survival--r3'),
       ('faa-wildlife-strike-substantial-damage-retry-1','faa-wildlife-strike-substantial-damage--r1')]
class Spy:
 def __init__(self,**kw):self.kw=kw
 def set_params(self,**kw):self.kw.update(kw);return self
 def fit(self,X,y,**kw):self.matrix=X.copy();self.labels=np.asarray(y).copy();return self
xgb.XGBClassifier=Spy

def captured(model,m,y):
 a=model['model'].matrix
 if isinstance(a,pd.DataFrame): ids=a.index.to_numpy(); values=a.to_numpy(dtype=float)
 else:
  assert m.__name__=='mapped_faa', 'No inspected mapping for NumPy matrices'
  ids=np.concatenate([np.arange(len(y)),np.sort(np.random.RandomState(42).choice(len(y),int(m.SIZE_MASK*len(y)),replace=False))])
  values=np.asarray(a,dtype=float)
 assert len(ids)==len(values) and np.array_equal(model['model'].labels,y[ids])
 return ids,values

reports=[]
for execution,rid in CASES:
 study=ROOT/'.local/studies'/execution;file=study/'evidence/frozen'/rid/'train.py'
 ds=rid.rsplit('--r',1)[0];rel=study/'.study/releases'/ds
 q=json.loads((rel/'reproduction/construction.json').read_text())['quality'];meta=json.loads((rel/'extract/meta.json').read_text())
 blocked=set(sum([q.get(k,[]) for k in ['id_columns','carry_columns','post_hoc_columns','label_source_columns']],[])+[q['target']])
 cols=[c for c in q['features'] if c not in blocked]
 df=pd.read_csv(rel/'extract/public/train.csv');X=df[cols];y=(df[meta['target']]==meta.get('positive_label',1)).astype(int).to_numpy()
 spec=importlib.util.spec_from_file_location('mapped_faa' if execution.startswith('faa-') else 'mapped_frame',file)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 fitted=m.fit(X,y,seed=42,threads=5);ids,A=captured(fitted,m,y)
 chosen=[int(ids[0]),int(ids[len(ids)//2])];checks=[]
 for idx in sorted(set(chosen)):
  y2=y.copy();y2[idx]=1-y2[idx]
  ids2,B=captured(m.fit(X,y2,seed=42,threads=5),m,y2)
  a=A[ids==idx];b=B[ids2==idx]
  common=min(len(a),len(b));changed=int((~np.isclose(a[:common],b[:common],rtol=0,atol=1e-10,equal_nan=True)).sum())
  checks.append({'source_row':idx,'original_copies':len(a),'perturbed_copies':len(b),'compared_copies':common,'changed_own_feature_cells':changed,'row_mapping_changed':not np.array_equal(ids,ids2)})
 r={'execution':execution,'run':rid,'frozen_code_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'full_training_rows':len(y),'fitted_rows':len(ids),'unique_source_rows_in_fit':len(set(ids)),'mapping':'preserved DataFrame index' if isinstance(fitted['model'].matrix,pd.DataFrame) else 'original rows plus fixed-seed SIZE_MASK subset','captured_labels_match_mapping':True,'checks':checks,'scope':'Two retained source rows, including copies. Label-dependent row selection is recorded separately from own-label feature encoding. No trees fit and no scores computed.'}
 reports.append(r);(OUT/'row-mapped-training-probes.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(r),flush=True)
