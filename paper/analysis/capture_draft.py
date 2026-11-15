"""Capture compact, immutable inputs for the first draft. Not a study rerun."""
import datetime,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'paper/analysis/draft-inputs.json'
if OUT.exists():raise SystemExit('Draft inputs already captured; preserve the snapshot.')
paths=['evidence/costs/2026-11-15/summary.json','evidence/costs/2026-11-15/inputs/cohort.json','evidence/costs/2026-11-15/inputs/summary.json','evidence/costs/2026-11-15/inputs/attempts_new_admissions.json','evidence/costs/2026-11-15/inputs/attempts_carry_in.json','evidence/costs/2026-11-15/inputs/rates.json','evidence/retries/plan.json']
cohort=json.loads((ROOT/paths[1]).read_text())
for r in cohort:
 ds=r['dataset']; paths.append(f'evidence/consumer/{ds}/results/summary.json')
 for f in ('bootstrap.json','training-feature-probes.json','artifact-probes.json'):
  p=f'evidence/reviews/{ds}/post/{f}'
  if (ROOT/p).exists():paths.append(p)
 p=f'evidence/reviews/{ds}/cluster.json'
 if (ROOT/p).exists():paths.append(p)
data={p:json.loads((ROOT/p).read_text()) for p in paths}
manifest_checks={}
for r in cohort:
 ds=r['dataset'];p=ROOT/'.local/studies'/ds/'.study/releases'/ds/'MANIFEST.json'
 m=json.loads(p.read_text());manifest_checks[ds]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'qualification':m.get('qualification'),'keys':list(m)}
x={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},'data':data,'manifest_checks':manifest_checks}
OUT.write_text(json.dumps(x,indent=2)+'\n')
print('Captured',len(paths),'compact files')
print(json.dumps(manifest_checks,indent=2))
