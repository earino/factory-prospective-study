"""Aggregate retained review records and adjudicated responses, without model calls."""
import collections,gzip,json
from pathlib import Path
from verify import events
BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def decoded(value):
 if isinstance(value,str):
  try:return json.loads(value)
  except json.JSONDecodeError:return value
 return value

def summarize():
 schedule=read(BASE/'schedule.json')['runs'];results=[];totals=collections.Counter();bytask=collections.defaultdict(collections.Counter);tool_inventory=[]
 for r in schedule:
  d=BASE/'runs'/r['run_id'];finish=read(d/'finished.json');start=read(d/'started.json');records=read(d/'session-records.json')
  usage=collections.Counter();tasks=collections.defaultdict(collections.Counter)
  for item in records['session_model_usage']:
   kind='title' if item['task']=='title_generation' else 'review'
   for field in ['api_call_count','input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','reasoning_tokens']:
    usage[field]+=item.get(field) or 0;tasks[kind][field]+=item.get(field) or 0;bytask[kind][field]+=item.get(field) or 0
  for k,v in usage.items():totals[k]+=v
  calls=[]
  for m in records['messages']:
   for call in decoded(m.get('tool_calls')) or []:
    f=call.get('function',call);name=f.get('name');args=decoded(f.get('arguments',{}))
    calls.append({'name':name,'arguments':args});assert name in ['web_search','web_extract'],name
  tool_inventory.append({'run_id':r['run_id'],'calls':calls})
  wire_usage=collections.Counter();models=set();chat_requests=0
  for request in (d/'wire').glob('*.request.json'):
   body=read(request)
   if 'messages' not in body:continue
   chat_requests+=1
   response=request.with_name(request.name.replace('.request.json','.response.body'))
   if not response.exists():response=Path(str(response)+'.gz')
   if not response.exists():continue
   for e in events(response):
    if e.get('model'):models.add(e['model'])
    u=e.get('usage')
    if u:
     wire_usage['reported_calls']+=1
     wire_usage['prompt_tokens']+=u.get('prompt_tokens',0)
     wire_usage['completion_tokens']+=u.get('completion_tokens',0)
     wire_usage['cached_prompt_tokens']+=u.get('prompt_tokens_details',{}).get('cached_tokens',0)
  # Preserve a legible decision separately from valid machine-readable output.
  response_text=(d/'response.txt').read_text()
  try:
   obj,_=json.JSONDecoder().raw_decode(response_text[response_text.index('{'):])
   assert obj['verdict'] in ['accept','repair','reject']
   structured={'valid_json':True,'parsed_verdict':obj['verdict'],'error':None}
  except (ValueError,KeyError,AssertionError) as error:
   structured={'valid_json':False,'parsed_verdict':None,'error':str(error)}
  results.append({**r,'finished':finish,'structured_output':structured,'started':start['started_utc'],'usage':dict(usage),'tasks':{k:dict(v) for k,v in tasks.items()},'tool_calls':len(calls),'wire_chat_requests':chat_requests,'wire_usage':dict(wire_usage),'response_model_ids':sorted(models)})
 summary={'scheduled_reviews':len(schedule),'completed_processes':len(results),'with_final_response':sum(r['finished']['has_response'] for r in results),'timeouts':sum(r['finished']['timeout'] for r in results),'nonzero_exits':sum(r['finished']['exit_code']!=0 for r in results),'usage':dict(totals),'usage_by_task':{k:dict(v) for k,v in bytask.items()},'runs':results,'tool_calls':sum(r['tool_calls'] for r in results),'elapsed_session_seconds':sum(r['finished']['elapsed_seconds'] for r in results),'worker_seconds':0}
 starts=[read(BASE/'runs'/r['run_id']/'process.json')['started_epoch'] for r in schedule]
 summary['batch_wall_seconds']=max(s+r['finished']['elapsed_seconds'] for s,r in zip(starts,results))-min(starts)
 summary['wire_prompt_tokens']=sum(r['wire_usage'].get('prompt_tokens',0) for r in results)
 summary['wire_completion_tokens']=sum(r['wire_usage'].get('completion_tokens',0) for r in results)
 summary['wire_cached_prompt_tokens']=sum(r['wire_usage'].get('cached_prompt_tokens',0) for r in results)
 # Hermes input tokens exclude cache reads; OpenAI wire prompt tokens include them.
 summary['wire_and_session_usage_agree']=(summary['wire_prompt_tokens']==totals['input_tokens']+totals['cache_read_tokens'] and summary['wire_completion_tokens']==totals['output_tokens'])
 (BASE/'results').mkdir(exist_ok=True)
 (BASE/'results/usage.json').write_text(json.dumps(summary,indent=2)+'\n')
 (BASE/'results/tool-inventory.json').write_text(json.dumps(tool_inventory,indent=2)+'\n')
 assessments=BASE/'assessment/assessments.json'
 if assessments.exists():
  mapping=read(BASE/'assessment/mapping.json');rows=read(assessments)['rows'];byrun={mapping[a['blind_id']]:a for a in rows}
  cells=[]
  for case in ['original','consistent']:
   for condition in ['original_packet','complete_packet','explicit_comparison']:
    cell=[byrun[r['run_id']] for r in schedule if (r['case'],r['condition'])==(case,condition)]
    assert len(cell)==5
    for a in cell:
     assert all(a[k] is not None for k in ['full_detection','false_contradiction','partial_selection_finding','verdict','ambiguous']),a['blind_id']
     if a['full_detection'] or a['false_contradiction'] or a['partial_selection_finding']:assert a['supporting_excerpts']
     for excerpt in a['supporting_excerpts']:assert excerpt in (BASE/'assessment'/f"{a['blind_id']}.txt").read_text(),a['blind_id']
    run_cell=[r for r in results if (r['case'],r['condition'])==(case,condition)]
    cells.append({'case':case,'condition':condition,'n':5,'completed_responses':len(cell),'full_detection':sum(a['full_detection'] for a in cell),'false_contradiction':sum(a['false_contradiction'] for a in cell),'partial_selection_finding':sum(a['partial_selection_finding'] for a in cell),'ambiguous':sum(a['ambiguous'] for a in cell),'stated_decisions':dict(collections.Counter(a['verdict'] for a in cell)),'valid_json_decisions':dict(collections.Counter(r['structured_output']['parsed_verdict'] for r in run_cell if r['structured_output']['valid_json'])),'malformed_json':sum(not r['structured_output']['valid_json'] for r in run_cell)})
  (BASE/'results/outcomes.json').write_text(json.dumps({'cells':cells,'scoring':'See PROTOCOL.md and assessment/assessments.json; counts are descriptive.'},indent=2)+'\n')
 return summary
if __name__=='__main__':
 s=summarize();print(json.dumps({k:v for k,v in s.items() if k!='runs'},indent=2))
