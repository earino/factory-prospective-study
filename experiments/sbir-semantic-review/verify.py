"""Verify frozen evidence and run capture; no network or model calls."""
import argparse,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def events(p):
 text=p.read_text()
 try:
  yield json.loads(text);return
 except json.JSONDecodeError:pass
 for line in text.splitlines():
  if line.startswith('data: '):
   try:yield json.loads(line[6:])
   except json.JSONDecodeError:pass

def verify(complete=False):
 checks={}
 for name,digest in read(BASE/'freeze.json')['files'].items():assert sha(BASE/name)==digest,name
 inputs=read(BASE/'inputs/manifest.json')
 for name,digest in inputs['files'].items():assert sha(BASE/name)==digest,name
 for name,digest in inputs['submitted_artifact_hashes'].items():assert sha(ROOT/name)==digest,name
 checks['frozen_files']=len(inputs['files']);checks['submitted_artifacts_unchanged']=True
 schedule=read(BASE/'schedule.json')['runs'];assert len(schedule)==30
 from collections import Counter
 assert set(Counter((r['case'],r['condition']) for r in schedule).values())=={5}
 assert len({r['run_id'] for r in schedule})==30
 prompt=(BASE/'inputs/historical/evaluate-1/prompt.txt').read_bytes()
 assert (BASE/'inputs/prompts/original--original_packet.txt').read_bytes()==prompt
 original=read(BASE/'inputs/cases/original-packet.json');consistent=read(BASE/'inputs/cases/consistent-packet.json')
 assert original['construction_code']==consistent['construction_code']==(BASE/'inputs/build.py').read_text()
 for k in original['measurement']:
  if k!='evaluation_contract':assert original['measurement'][k]==consistent['measurement'][k]
 checks['comparison_preserves_builder_and_check_measurements']=True
 result=[];session_ids=[]
 for r in schedule:
  d=BASE/'runs'/r['run_id']
  if not (d/'finished.json').exists():
   if complete:raise AssertionError('Missing finished record: '+r['run_id'])
   continue
  assert sha(d/'prompt.txt')==sha(BASE/r['prompt'])
  records=read(d/'session-records.json');sessions=records['sessions'];assert len(sessions)==1
  session_ids.append(sessions[0]['id'])
  wires=[]
  for req in sorted((d/'wire').glob('*.request.json')):
   body=read(req)
   if 'messages' not in body:continue
   assert body['model']=='deepseek-v4.1-flash'
   substantive='tools' in body
   if substantive:
    assert sorted(t['function']['name'] for t in body['tools'])==['web_extract','web_search']
    user=[m for m in body['messages'] if m['role']=='user']
    assert user[0]['content']==(d/'prompt.txt').read_text()
   response=req.with_name(req.name.replace('.request.json','.response.body'))
   parsed=list(events(response)) if response.exists() else []
   models={e['model'] for e in parsed if e.get('model')}
   assert not models or models=={'deepseek-v4.1-flash'},models
   wires.append({'file':str(req.relative_to(BASE)),'substantive':substantive,'response_model_ids':sorted(models)})
  assert wires, r['run_id']
  assert any(x['substantive'] for x in wires),r['run_id']
  result.append({'run_id':r['run_id'],'finished':read(d/'finished.json'),'wire_calls':wires})
 assert len(session_ids)==len(set(session_ids))
 checks.update(finished_runs=len(result),fresh_session_ids=len(set(session_ids)),runs=result)
 return checks
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--complete',action='store_true');args=a.parse_args()
 out=verify(args.complete);(BASE/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='runs'},indent=2))
