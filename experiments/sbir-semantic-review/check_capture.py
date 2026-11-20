"""Check saved API/session provenance and archive integrity without inference."""
import gzip,hashlib,json
from pathlib import Path
from verify import events
BASE=Path(__file__).resolve().parent

def check():
 initial=BASE/'assessment/initial-assessment-freeze.json'
 if initial.exists():
  frozen=json.loads(initial.read_text())
  assert hashlib.sha256((initial.parent/frozen['file']).read_bytes()).hexdigest()==frozen['sha256']
  mapping=json.loads((initial.parent/'mapping.json').read_text())
  observations=json.loads((initial.parent/frozen['file']).read_text())['rows']
  assert len(observations)==30 and len(set(mapping.values()))==30
  for row in observations:
   response=(initial.parent/(row['blind_id']+'.txt')).read_bytes()
   assert hashlib.sha256(response).hexdigest()==row['response_sha256']
   assert response==(BASE/'runs'/mapping[row['blind_id']]/'response.txt').read_bytes()
 archives=json.loads((BASE/'wire-archive.json').read_text())
 for row in archives:
  p=BASE/row['path'];data=p.read_bytes();raw=gzip.decompress(data)
  assert hashlib.sha256(data).hexdigest()==row['compressed_sha256'],str(p)
  assert hashlib.sha256(raw).hexdigest()==row['uncompressed_sha256'],str(p)
  assert len(raw)==row['uncompressed_bytes'],str(p)
  source=Path(str(p)[:-3])
  if source.exists():assert source.read_bytes()==raw,str(p)
 tools=[];routes=[];prompts=[]
 for d in sorted((BASE/'runs').glob('*')):
  if not (d/'finished.json').exists():continue
  data=json.loads((d/'session-records.json').read_text())
  for session in data['sessions']:
   assert session['source']=='oneshot'
   assert session['model']=='deepseek-v4.1-flash'
   assert session['billing_provider']=='ollama-cloud'
   requests=[json.loads(p.read_text()) for p in sorted((d/'wire').glob('*.request.json'))]
   first=next(r for r in requests if 'tools' in r)
   system=[m['content'] for m in first['messages'] if m['role']=='system']
   assert system,d.name
   prompts.append({'run_id':d.name,'system_prompt_sha256':hashlib.sha256(json.dumps(system).encode()).hexdigest(),'source':'captured HTTP request; database system_prompt may be null','cwd':session['cwd']})
  replies=[]
  for req in sorted((d/'wire').glob('*.request.json')):
   payload=json.loads(req.read_text())
   if 'tools' not in payload:continue
   body=req.with_name(req.name.replace('.request.json','.response.body'))
   if not body.exists():body=Path(str(body)+'.gz')
   if not body.exists():continue
   chunks=[]
   for event in events(body):
    for choice in event.get('choices',[]):
     value=choice.get('delta',choice.get('message',{})).get('content')
     if isinstance(value,str):chunks.append(value)
   if chunks:replies.append(''.join(chunks))
  if (d/'response.txt').exists():
   assert replies and replies[-1].strip()==(d/'response.txt').read_text().strip(),('Wire/final response mismatch',d.name)
  for m in data['messages']:
   if m['role']=='tool':
    assert m['tool_name'] in ['web_search','web_extract'],m['tool_name']
    tools.append({'run_id':d.name,'name':m['tool_name'],'bytes':len(m['content'].encode())})
  for row in data['session_model_usage']:
   assert row['model']=='deepseek-v4.1-flash'
   assert row['billing_provider']=='ollama-cloud'
   routes.append({'run_id':d.name,'model':row['model'],'provider':row['billing_provider'],'task':row['task']})
 return {'lossless_archives_checked':len(archives),'tool_results':tools,'recorded_routes':routes,'system_prompts':prompts,'scope':'No headers were captured. Model identifiers are provider/runtime reports, not independent model attestation.'}
if __name__=='__main__':
 result=check();(BASE/'capture-checks.json').write_text(json.dumps(result,indent=2)+'\n');print('Checked',result['lossless_archives_checked'],'lossless archives and',len(result['system_prompts']),'session prompts')
