"""Check the short-paper record inputs independently of rendered prose."""
from pathlib import Path
from datetime import datetime
from collections import Counter
import hashlib
import json
import re
import statistics

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'paper-agent27-short'
def read(p): return json.loads((ROOT/p).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
snapshot=read('paper/analysis/final-inputs-2026-11-16.json')
release=read('paper-agent27-short/analysis/release-records.json')
assert sha(ROOT/release['snapshot'])==release['snapshot_sha256']
cost=read('evidence/costs/2026-11-16/summary.json')
start,end=map(datetime.fromisoformat,[cost['window_start'],cost['cutoff']])
all_attempts=[]
for f in ['attempts_carry_in.json','attempts_new_admissions.json']:
 all_attempts+=read('evidence/costs/2026-11-16/inputs/'+f)
attempts=[a for a in all_attempts if start<=datetime.fromisoformat(a['started'])<end]
assert len({a['id'] for a in attempts})==len(attempts)==540
counts=Counter((a['stage'],a['status']) for a in attempts)
assert counts['discover','retry']==101 and counts['build','retry']==260 and counts['evaluate','repair']==21
milestones={s:len({a['candidate'] for a in attempts if a['stage']==s and a['status']=='done'}) for s in ['discover','build','evaluate','publish']}
assert milestones=={'discover':54,'build':18,'evaluate':14,'publish':14}
assert len(snapshot['production_cohort'])==14 and len(snapshot['consumer_cohort'])==12
latencies=[]
for r,original in zip(release['records'],snapshot['production_cohort'],strict=True):
 assert r['dataset']==original['dataset'] and r['created']==original['created'] and r['published_at']==original['published_at']
 latency=(datetime.fromisoformat(r['published_at'])-datetime.fromisoformat(r['created'])).total_seconds()/60
 assert abs(latency-r['latency_minutes'])<1e-9
 latencies.append(latency)
 if r['review_path']: assert sha(ROOT/r['review_path'])==r['review_sha256']
assert [round(min(latencies)),round(max(latencies)),round(statistics.median(latencies))]==[40,231,109]
consumer={}
for dataset,selected in snapshot['analysis_selection'].items():
 path=snapshot.get('consumer_overrides',{}).get(dataset,f'evidence/consumer/{selected}/results/summary.json')
 summary=snapshot['data'][path]
 frozen={r['id'] for r in summary['outcomes'] if r['status']=='frozen' and r['dataset']==dataset}
 scored={r['id'] for r in summary['scores'] if r.get('kind')=='agent' and r['dataset']==dataset and r.get('holdout_rows',0)>0 and r.get('holdout_auc') is not None}
 assert len(frozen)==3 and frozen==scored, dataset
 consumer[dataset]={'scored_models':len(scored),'summary':path}
assert len(consumer)==12
for r in release['records']:
 assert (r['consumer']=='Completed')==(r['dataset'] in consumer)
 assert (r['review_path'] is None)==(r['dataset'] not in consumer)
assert round(cost['elapsed_hours'],2)==81.53
assert [round(v,2) for v in cost['factory_total_time_priced_usd_range']]==[38.23,38.33]
assert [round(v,2) for v in cost['factory_time_priced_usd_per_release_range']]==[2.73,2.74]
assert round(cost['factory_peak_usd_per_release'],2)==3.92
stage=read('paper-agent27-short/analysis/stage-costs.json')
for path,digest in stage['sources'].items(): assert sha(ROOT/path)==digest
for i,key in enumerate(['total_low_usd','total_high_usd']):
 assert abs(sum(r[key] for r in stage['stages'].values())-cost['factory_total_time_priced_usd_range'][i])<1e-8
assert round(stage['build_share_at_midpoint']*100)==64
# Actual review packet and public-builder identity, without rewriting the old report.
p=ROOT/'paper/analysis/final-2026-11-16/sbir-acceptance'
retrieval=json.loads((p/'retrieval.json').read_text())
for name,digest in retrieval['sha256'].items(): assert sha(p/name)==digest
manifest=json.loads((p/'published-manifest.json').read_text())
builder=json.loads((p/'build-3/response.json').read_text())['build_py']
assert hashlib.sha256(builder.encode()).hexdigest()==manifest['assets']['reproduction/build.py']['sha256']
prompt=(p/'evaluate-1/prompt.txt').read_text()
packet=json.loads(prompt[prompt.index('{"construction_code":'):])
assert packet['construction_code']==builder
assert 'no outcome field is used to select rows' not in prompt
assert 'no outcome field is used to select rows' in (p/'published-construction.json').read_text()
response=json.loads((p/'evaluate-1/response.json').read_text())
assert response['verdict']=='accept' and response['findings']==[]
assert 'Population matches the rule' in response['reason']
assert 'unknown/missing phases in a window are excluded' in response['reason']
# The first-publication trace is taken from its original stage records.
trace=[a for a in attempts if a['candidate']=='source-000048']
assert len(trace)==10
assert Counter((a['stage'],a['status']) for a in trace)=={('discover','done'):1,('build','retry'):2,('build','done'):3,('evaluate','repair'):2,('evaluate','done'):1,('publish','done'):1}
assert 'letter-suffixed' in next(a['result'] for a in trace if a['stage']=='evaluate' and a['ordinal']==2)
preserved=read('paper-agent27-short/analysis/long-paper-preservation.json')
for path,digest in preserved.items(): assert sha(ROOT/path)==digest, f'Long-paper file changed: {path}'
disclosure=read('paper-agent27-short/analysis/disclosure-review.json')
assert {r['dataset'] for r in disclosure['records']}==set(consumer)
condition_statuses=Counter()
for row in disclosure['records']:
 assert sha(ROOT/row['pin_path'])==row['pin_sha256']
 pin=read(row['pin_path'])
 assert pin[:3]==[row['dataset'],row['version'],row['huggingface_commit']]
 assert sha(ROOT/row['review_path'])==row['review_sha256']
 manifest=read(row['documents']['MANIFEST.json']['path'])
 assert row['documents']['MANIFEST.json']['sha256']==pin[3]
 for name,doc in row['documents'].items():
  assert sha(ROOT/doc['path'])==doc['sha256']
  if name!='MANIFEST.json': assert manifest['assets'][name]['sha256']==doc['sha256']
 for finding in row['findings']:
  if finding['category']=='condition': condition_statuses[finding['disclosure']]+=1
  for evidence in finding['evidence']:
   doc=ROOT/row['documents'][evidence['file']]['path']
   if 'pointer' in evidence:
    value=json.loads(doc.read_text())
    for part in evidence['pointer'].strip('/').split('/'):
     value=value[int(part)] if isinstance(value,list) else value[part]
    assert value==evidence['value']
   else: assert doc.read_text().splitlines()[evidence['line']-1]==evidence['quote']
 table_record=next(r for r in release['records'] if r['dataset']==row['dataset'])
 assert table_record['disclosure_findings']==row['findings']
assert dict(condition_statuses)=={'stated':5,'partly_stated':1}
assert disclosure['condition_counts']=={'total':6,'stated':5,'partly_stated':1}
concern_statuses=Counter(f['disclosure'] for r in disclosure['records'] for f in r['findings'] if f['category']=='concern')
assert dict(concern_statuses)=={'stated':1,'partly_stated':3,'not_found':4}
assert disclosure['concern_counts']=={'total':8,**dict(concern_statuses)}
tex=(OUT/'draft/main.tex').read_text()
for banned in ['presentation emphasis','we now focus','later paper','interim results','random-search','holdout AUC','BLOCKER.json','---','…']:
 assert banned.lower() not in tex.lower(), banned
citations=set()
for c in re.findall(r'\\cite\{([^}]+)\}',tex): citations.update(c.split(','))
assert len(citations)==13
report={'production_attempts':len(attempts),'milestones':milestones,'retry_counts':{'discovery':101,'build':260,'semantic_repair':21},
 'publications':14,'consumer_datasets':12,'scored_models_checked':sum(r['scored_models'] for r in consumer.values()),
 'consumer_summaries':consumer,'latency_min_max_median_minutes':[min(latencies),max(latencies),statistics.median(latencies)],
 'cost_range_usd':cost['factory_total_time_priced_usd_range'],'stage_costs_reconcile':True,'build_share_percent':stage['build_share_at_midpoint']*100,
 'sbir_original_files_verified':len(retrieval['sha256']),'first_release_trace_attempts':len(trace),'long_paper_files_preserved':len(preserved),'citations':sorted(citations),
 'disclosure_documents_checked':36,'disclosure_conditions':dict(condition_statuses),
 'disclosure_concerns':dict(concern_statuses),
 'disclosure_review_sha256':sha(OUT/'analysis/disclosure-review.json'),
 'manuscript_sha256':sha(OUT/'draft/main.tex'),
 'scope':'Recorded quantities, input identities, consumer completion, source-review identities and known wording checks. Does not mechanically establish semantic correctness of every sentence; manual claim and page reviews are separate.'}
(OUT/'analysis/record-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['publications','consumer_datasets','production_attempts','stage_costs_reconcile','long_paper_files_preserved']}))
