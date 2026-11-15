"""Add completed Seattle and railway recoveries; retain all prior snapshots."""
import datetime,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'paper/analysis/evening-inputs-2026-11-15.json'
if O.exists():raise SystemExit('Evening snapshot already exists; preserve it.')
paths=['queue.json','.local/worker.json'];selections={};overrides={};extra=[]
for ds in ['seattle-building-permit-completion','fra-form54-hazmat-release']:
 ex=ds+'-retry-1';selections[ds]=ex
 paths += [f'evidence/outcomes/{ex}.json',f'evidence/consumer/{ex}/results/summary.json',f'evidence/reviews/{ex}/cluster.json',f'evidence/reviews/{ex}/pinned-release.json']
 for name in ['bootstrap.json','training-feature-probes.json','artifact-probes.json','control-features.json','execution.json']:
  path=f'evidence/reviews/{ex}/post/{name}'
  if (R/path).exists():paths.append(path)
 for name in ['qualification.json','artifact-verification.json']:
  paths.append(f'paper/analysis/evening-2026-11-15/{ds}-{name}')
 extra += [f'evidence/reviews/{ex}/PRE-REVIEW.md',f'paper/analysis/evening-2026-11-15/{ds}-acceptance.txt']
ds='seattle-building-permit-completion'
for name in ['training-feature-probes.json','artifact-probes.json','control-features.json','provenance.json']:
 path='paper/analysis/evening-2026-11-15/seattle-probes/'+name;paths.append(path);overrides.setdefault(ds,{})[name]=path
paths.append('.local/studies/seattle-building-permit-completion-retry-1/.study/runs/seattle-building-permit-completion--r1/BLOCKER.json')
data={p:json.loads((R/p).read_text()) for p in paths}
O.write_text(json.dumps({'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'analysis_selection':selections,'review_overrides':overrides,'sources':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths+extra},'data':data},indent=2)+'\n');print(O)
