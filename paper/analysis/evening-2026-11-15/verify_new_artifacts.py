"""Verify existing worker reports against saved study artifacts; no new scoring."""
from pathlib import Path
import urllib.request,json,hashlib,tempfile,shutil,subprocess
R=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
for ds in ['seattle-building-permit-completion','fra-form54-hazmat-release']:
 study=R/'.local/studies'/(ds+'-retry-1');release=study/'.study/releases'/ds
 m=json.loads((release/'MANIFEST.json').read_text());url='https://github.com/earino/factory-'+ds+'/releases/download/'+m['version']+'/'
 tmp=Path(tempfile.mkdtemp(prefix='factory-paper-qualified-'));extract=tmp/'extract';extract.mkdir()
 for rel,src in [('public/train.csv',release/'extract/public/train.csv'),('public/eval.csv',release/'extract/public/eval.csv'),('meta.json',release/'extract/meta.json'),('private/holdout.csv',study/'.study/holdout'/ds/'holdout.csv')]:
  dest=extract/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
 report=OUT/(ds+'-qualification.json')
 for key in ['qualification.json','extract/quality.json','reproduction/qualify_dataset.py','reproduction/leakage_battery.py','reproduction/recovery_recipes.py','reproduction/artifact_scrub.py']:
  a=m['assets'][key];b=urllib.request.urlopen(url+a['asset_name'],timeout=30).read();assert hashlib.sha256(b).hexdigest()==a['sha256'],key
  dest=report if key=='qualification.json' else extract/'quality.json' if key=='extract/quality.json' else tmp/Path(key).name;dest.write_bytes(b)
 r=subprocess.run(['python3',str(tmp/'qualify_dataset.py'),'--accept',str(report),str(extract)],text=True,capture_output=True)
 (OUT/(ds+'-acceptance.txt')).write_text(r.stdout+r.stderr);print(r.stdout,r.stderr);r.check_returncode()
 (OUT/(ds+'-artifact-verification.json')).write_text(json.dumps({'release_tag':m['version'],'artifact_version':m['artifact_version'],'manifest_sha256':hashlib.sha256((release/'MANIFEST.json').read_bytes()).hexdigest(),'qualification_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),'accept_exit_code':r.returncode,'scope':'Rechecked original worker qualification against complete saved study splits and published quality descriptor; no construction, model fitting, or new qualification.'},indent=2)+'\n')
