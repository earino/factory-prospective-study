"""Freeze the November 15 consumer update without replacing the first draft inputs."""
import datetime,gzip,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'paper/analysis/update-inputs-2026-11-15.json'
if O.exists():raise SystemExit('Update already captured; preserve it.')
execution='faa-wildlife-strike-substantial-damage-retry-1'
paths=['queue.json','.local/worker.json',f'evidence/outcomes/{execution}.json',f'evidence/consumer/{execution}/results/summary.json']
paths += [f'evidence/reviews/{execution}/'+p for p in ['cluster.json','pinned-release.json','post/bootstrap.json','post/training-feature-probes.json','post/artifact-probes.json','post/control-features.json']]
paths += ['paper/analysis/update-2026-11-15/faa-artifact-verification.json','paper/analysis/update-2026-11-15/faa-qualification.json']
data={p:json.loads((R/p).read_text()) for p in paths}
snapshot='evidence/snapshots/20261115T165519Z.json.gz';d=json.loads(gzip.decompress((R/snapshot).read_bytes()))
data['public_snapshot']={k:d[k] for k in ['generated_at','modern']};data['public_snapshot']['modern'].pop('candidates',None)
extra=[snapshot,f'evidence/reviews/{execution}/PRE-REVIEW.md','paper/analysis/update-2026-11-15/faa-acceptance.txt','paper/analysis/draft-inputs.json']
O.write_text(json.dumps({'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'analysis_selection':{'faa-wildlife-strike-substantial-damage':execution},'sources':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths+extra},'data':data},indent=2)+'\n')
print(O)
