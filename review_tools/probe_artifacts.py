import os
"""Read-only selected-artifact probes; no fitting or new benchmark scores."""
import datetime,json,pickle,sys,os
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(os.environ['STUDY_ROOT']);OUT=Path(os.environ['REVIEW_OUT']); OUT.mkdir(parents=True,exist_ok=True)
def allowed(rid):
 q=json.loads((ROOT/'.study/runs'/rid/'release/reproduction/construction.json').read_text())['quality']
 blocked=set(q.get('id_columns',[])+q.get('carry_columns',[])+q.get('post_hoc_columns',[])+q.get('label_source_columns',[])+[q['target']])
 return [c for c in q['features'] if c not in blocked]

active=False;events=[]
def guard(event,args):
 if not active:return
 if event=='open':
  path=str(args[0]); dependency=path.startswith((sys.prefix+'/',sys.base_prefix+'/','/usr/share/zoneinfo/'))
  events.append({'event':event,'path':path,'dependency_read':dependency})
  if not dependency and not isinstance(args[0],int):raise RuntimeError('prepare attempted nondependency file read: '+path)
 elif event.startswith('socket.') or event.startswith('subprocess.') or event in ['os.system','os.chdir']:
  events.append({'event':event});raise RuntimeError('prepare attempted external operation: '+event)
sys.addaudithook(guard)
def concat(parts):return pd.concat(parts,ignore_index=True) if isinstance(parts[0],pd.DataFrame) else np.concatenate(parts,axis=0)
def matrix(z):
 if isinstance(z,pd.DataFrame):
  z=z.copy()
  for c in z:
   if isinstance(z[c].dtype,pd.CategoricalDtype):z[c]=z[c].cat.codes
 return np.asarray(z,dtype=float)
results=[]
for rid in json.loads((ROOT/'study.json').read_text())['order']:
 events.clear()
 d=ROOT/'evidence/frozen'/rid; a=pickle.loads((d/'model.pkl').read_bytes());rel=ROOT/'.study/runs'/rid/'release/extract';meta=json.loads((rel/'meta.json').read_text());df=pd.read_csv(rel/'public/eval.csv');X=df[allowed(rid)];idx=np.linspace(0,len(X)-1,min(25,len(X)),dtype=int);X=X.iloc[idx].reset_index(drop=True)
 def prep(z):
  global active
  active=True
  try:return a['prepare'](a['state'],z)
  finally:active=False
 try:
  B=prep(X);R=concat([prep(X.iloc[[i]].reset_index(drop=True)) for i in range(len(X))]);V=prep(X.iloc[::-1].reset_index(drop=True))
  record={'run':rid,'real_validation_rows_checked':len(X),'batch_equals_single_rows':bool(np.allclose(matrix(B),matrix(R),rtol=0,atol=0,equal_nan=True)),'reverse_order_invariant':bool(np.allclose(matrix(B),matrix(V)[::-1],rtol=0,atol=0,equal_nan=True)),'prepare_external_events':list(events),'n_jobs':a['state']['model'].get_params().get('n_jobs'),'feature_count':R.shape[1]}
  if rid.startswith('fdic'):
   cols=a['state'].get('cols') or a['state'].get('names');record['selected_feature_names']=cols
  results.append(record)
 except Exception as e:results.append({'run':rid,'error':repr(e),'prepare_external_events':list(events)})
 (OUT/'artifact-probes.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results[-1]),flush=True)
# Read comparator feature contract actually used.
controls=[]
for d in json.loads((ROOT/'study.json').read_text())['datasets']:
 a=pickle.loads((ROOT/'evidence/frozen'/(d+'--ordinary')/'model.pkl').read_bytes());controls.append({'dataset':d,'ordinary_features':a['state'].get('cols')})
(OUT/'control-features.json').write_text(json.dumps(controls,indent=2)+'\n')
