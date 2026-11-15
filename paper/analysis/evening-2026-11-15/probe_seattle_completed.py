"""Run original review probes on completed artifacts in a separate read-only view."""
from pathlib import Path
import json,tempfile,os,subprocess,hashlib
R=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'seattle-probes';OUT.mkdir(exist_ok=True)
root=R/'.local/studies/seattle-building-permit-completion-retry-1';config=json.loads((root/'study.json').read_text());order=config['order'];selected=[];excluded=[]
for rid in order:
 state=json.loads((root/'.study/states'/(rid+'.json')).read_text())
 if state['status']=='frozen':
  assert (root/'evidence/frozen'/rid/'model.pkl').exists();selected.append(rid)
 else:excluded.append({'run':rid,'status':state['status']})
assert len(selected)==2 and len(excluded)==1
config['order']=selected
view=Path(tempfile.mkdtemp(prefix='factory-paper-review-view-'))
for name in ['.study','evidence']:(view/name).symlink_to(root/name,target_is_directory=True)
(view/'study.json').write_text(json.dumps(config))
env=os.environ.copy();env.update(STUDY_ROOT=str(view),REVIEW_OUT=str(OUT))
records=[]
for name in ['probe_artifacts.py','probe_all_training_features.py']:
 tool=R/'review_tools'/name
 with (OUT/(name+'.log')).open('w') as log:r=subprocess.run([str(root/'.study/venv/bin/python'),str(tool)],env=env,stdout=log,stderr=subprocess.STDOUT)
 records.append({'tool':name,'sha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'exit_code':r.returncode});r.check_returncode()
(OUT/'provenance.json').write_text(json.dumps({'study':str(root.relative_to(R)),'included_runs':selected,'excluded_runs':excluded,'method':'Temporary view with copied study.json order restricted to already frozen runs; original .study and evidence read through symlinks. No original files changed, no tree fitting or scoring.','tools':records},indent=2)+'\n')
print((OUT/'training-feature-probes.json').read_text());print((OUT/'artifact-probes.json').read_text())
