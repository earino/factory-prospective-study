"""Isolated Hermes reviewer runner. Credentials stay outside the repository."""
import base64, argparse, concurrent.futures, hashlib, json, os, signal, sqlite3, subprocess, tempfile, time
from pathlib import Path
BASE=Path(__file__).resolve().parent
HERMES=Path.home()/'.hermes/hermes-agent'
PYTHON=HERMES/'venv/bin/python'
MODEL='deepseek-v4.1-flash'
def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=lambda v:{"base64":base64.b64encode(v).decode()} if isinstance(v,bytes) else str(v))+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def credentials():
 # Read only the inference credential. Never copy the user's general environment/config.
 result=subprocess.run([str(PYTHON),'-c',"from dotenv import dotenv_values;import json;from pathlib import Path;print(json.dumps({'OLLAMA_API_KEY':dotenv_values(Path.home()/'.hermes/.env').get('OLLAMA_API_KEY')}))"],capture_output=True,text=True,check=True)
 data=json.loads(result.stdout);assert data['OLLAMA_API_KEY'],'Missing Ollama inference key'
 return data
CONFIG='''model:
  default: deepseek-v4.1-flash
  provider: ollama-cloud
web:
  backend: firecrawl
agent:
  max_turns: 12
'''
def env_for(home):
 allowed=['PATH','HOME','USER','LANG','LC_ALL','TMPDIR','SSL_CERT_FILE','SSL_CERT_DIR']
 env={k:os.environ[k] for k in allowed if k in os.environ}
 env.update(credentials());env['HERMES_HOME']=str(home);env['PYTHONPATH']=str(HERMES)
 env['PYTHONUNBUFFERED']='1'
 return env

def export_db(home,out):
 p=home/'state.db'
 if not p.exists():return {'sessions':[], 'usage':[], 'messages':[]}
 con=sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
 tables={r[0] for r in con.execute("select name from sqlite_master where type='table'")}
 records={}
 for name in ['sessions','session_model_usage','messages']:
  records[name]=[dict(r) for r in con.execute('select * from '+name)] if name in tables else []
 con.close()
 dump(out/'session-records.json',records)
 return records

def run_one(run_id,prompt,seconds=600):
 out=BASE/('smoke' if run_id.startswith('smoke') else 'runs')/run_id
 out.mkdir(parents=True,exist_ok=False)
 (out/'prompt.txt').write_bytes(prompt.read_bytes())
 with tempfile.TemporaryDirectory(prefix='sbir-review-private-') as td:
  home=Path(td)/'home';work=Path(td)/'work';home.mkdir(mode=0o700);work.mkdir(mode=0o700)
  (home/'config.yaml').write_text(CONFIG)
  env=env_for(home)
  env['SBIR_CAPTURE_DIR']=str((out/'wire').resolve())
  cmd=[str(PYTHON),str(BASE/'capture_runtime.py'),str(HERMES/'hermes'),'chat','--oneshot','-Q','--query-file',str((out/'prompt.txt').resolve()),'--source','oneshot','--model',MODEL,'--provider','ollama-cloud','--ignore-rules','--in',str(work),'-t','web','--max-turns','12','--run-budget',str(seconds)]
  started=time.time();dump(out/'started.json',{'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'requested_model':MODEL,'provider':'ollama-cloud','max_turns':12,'seconds':seconds,'prompt_sha256':sha(prompt),'config':CONFIG,'runtime_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERMES,text=True).strip()})
  with (out/'stdout.txt').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
   proc=subprocess.Popen(cmd,cwd=work,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
   dump(out/'process.json',{'pid':proc.pid,'parent_pid':os.getpid(),'started_epoch':started})
   timed_out=False
   try:code=proc.wait(timeout=seconds+45)
   except subprocess.TimeoutExpired:
    timed_out=True;os.killpg(proc.pid,signal.SIGTERM)
    try:code=proc.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);code=proc.wait()
  # Fail closed if runtime output ever contains the inference credential.
  for f in out.rglob('*'):
   if f.is_file() and env['OLLAMA_API_KEY'].encode() in f.read_bytes():
    f.write_bytes(f.read_bytes().replace(env['OLLAMA_API_KEY'].encode(),b'[REDACTED INFERENCE CREDENTIAL]'))
    raise RuntimeError('Credential appeared in output; redacted; do not proceed')
  records=export_db(home,out)
  assistants=[m for m in records.get('messages',[]) if m.get('role')=='assistant' and m.get('content') and not m.get('tool_calls')]
  if assistants:(out/'response.txt').write_text(assistants[-1]['content'])
  dump(out/'finished.json',{'exit_code':code,'timeout':timed_out,'elapsed_seconds':round(time.time()-started,3),'session_count':len(records.get('sessions',[])),'has_response':bool(assistants)})
  print(run_id,'finished',code,round(time.time()-started,1),flush=True)
 return code

def preflight():
 with tempfile.TemporaryDirectory(prefix='sbir-preflight-') as td:
  home=Path(td);(home/'config.yaml').write_text(CONFIG);env=env_for(home)
  probe="from model_tools import get_tool_definitions;import json;d=get_tool_definitions(enabled_toolsets=['web'],quiet_mode=True);print(json.dumps(d))"
  p=subprocess.run([str(PYTHON),'-c',probe],env=env,cwd=HERMES,text=True,capture_output=True,timeout=60)
  print('tool probe exit',p.returncode)
  if p.returncode:print(p.stderr[-3000:]);raise SystemExit(1)
  defs=json.loads(p.stdout.strip().splitlines()[-1]);names=sorted(d['function']['name'] for d in defs)
  print('Tools',names);assert names==['web_extract','web_search'],names
  dump(BASE/'runtime/tool-definitions.json',defs)
  dump(BASE/'runtime/preflight.json',{'tool_names':names,'runtime_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERMES,text=True).strip(),'config':CONFIG,'credentials':'OLLAMA_API_KEY from local Hermes environment; no publishing or production credentials passed','historical_difference':'Current local Hermes runtime and keyless Firecrawl web backend; original used hosted Hermes and web gateway. Original system prompt/config is not fully retained.'})

def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['preflight','smoke','run']);args=parser.parse_args()
 if args.action=='preflight':return preflight()
 if args.action=='smoke':
  p=BASE/'smoke-prompt.txt';p.write_text('Use web_extract to read https://www.sbir.gov/data-resources/data-dictionary/award . Return JSON with the page title, whether extraction succeeded, and the documented meaning of the Phase field. Do not search for or review any dataset.');return run_one('smoke-03',p,180)
 frozen=json.loads((BASE/'inputs/manifest.json').read_text())
 for path,expected in frozen['files'].items():assert sha(BASE/path)==expected,path
 schedule=json.loads((BASE/'schedule.json').read_text())['runs']
 pending=[]
 for r in schedule:
  p=BASE/'runs'/r['run_id']
  if p.exists():
   if not (p/'finished.json').exists():raise SystemExit('Unfinished run requires inspection: '+r['run_id'])
  else:pending.append(r)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(run_one,r['run_id'],BASE/r['prompt']) for r in pending]
  for f in concurrent.futures.as_completed(futures):f.result()
if __name__=='__main__':main()
