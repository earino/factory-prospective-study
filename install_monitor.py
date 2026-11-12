#!/usr/bin/env python3
"""Install this study's bounded macOS monitor and idle-sleep assertion."""
import datetime as dt,json,os,plistlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'protocol.json').read_text())
end=dt.datetime.fromisoformat(p['paper_ready_due'].replace('Z','+00:00'))+dt.timedelta(hours=1)
seconds=int((end-dt.datetime.now(dt.timezone.utc)).total_seconds())
if seconds<=0:raise SystemExit('Study window has ended; no schedules installed')
folder=Path.home()/'Library/LaunchAgents';folder.mkdir(parents=True,exist_ok=True)
logs=ROOT/'.local/logs';logs.mkdir(parents=True,exist_ok=True)
base='org.earino.factory-prospective-study'
path=str(Path.home()/'.local/bin')+':/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Library/TeX/texbin'
records=[]
for label,args,extra in [
 (base,[sys.executable,str(ROOT/'controller.py'),'tick'],{'StartInterval':300}),
 (base+'.awake',[sys.executable,str(ROOT/'controller.py'),'awake'],{})]:
 spec={'Label':label,'ProgramArguments':args,'WorkingDirectory':str(ROOT),'RunAtLoad':True,
       'EnvironmentVariables':{'PATH':path},'StandardOutPath':str(logs/(label+'.out.log')),
       'StandardErrorPath':str(logs/(label+'.err.log')),**extra}
 file=folder/(label+'.plist')
 if file.exists():raise SystemExit(f'Already installed: {file}; inspect before replacing')
 with file.open('wb') as f:plistlib.dump(spec,f)
 subprocess.run(['launchctl','bootstrap',f'gui/{os.getuid()}',str(file)],check=True)
 records.append({'label':label,'path':str(file),'spec':spec})
(ROOT/'evidence/setup/launchd.json').write_text(json.dumps({'installed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'end':end.isoformat(),'agents':records},indent=2)+'\n')
print(json.dumps(records,indent=2))
