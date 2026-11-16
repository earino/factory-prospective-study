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
accounting=read('paper-agent27-short/analysis/attempt-accounting.json')
for path,digest in accounting['sources'].items(): assert sha(ROOT/path)==digest
assert (accounting['window_start'],accounting['cutoff'])==(cost['window_start'],cost['cutoff'])
for stage_name,outcomes in accounting['stage_outcomes'].items():
 for outcome,count in outcomes.items(): assert counts[stage_name,outcome]==count
assert accounting['stage_totals']=={'discover':185,'build':299,'evaluate':41,'publish':15}
assert accounting['outcome_totals']=={'done':119,'retry':366,'repair':21,'defer':31,'reject':2,'running':1}
assert sum(accounting['stage_totals'].values())==sum(accounting['outcome_totals'].values())==540
retry_ids={a['id'] for a in attempts if a['status']=='retry'}
assert {r['attempt'] for r in accounting['retry_records']}==retry_ids
assert len(accounting['retry_records'])==len(retry_ids)==366
assert Counter(r['category'] for r in accounting['retry_records'])==accounting['retry_categories']=={
 'worker_outcome':206,'model_invocation':98,'proposal_or_controller_validation':61,'publication_reconciliation':1}
attempt_by_id={a['id']:a for a in attempts}
jobs={j['attempt']:j for j in read('evidence/costs/2026-11-16/inputs/jobs_ledger.json')}
for r in accounting['retry_records']:
 original=attempt_by_id[r['attempt']]
 assert original['stage']==r['stage']
 # Inspect the original result separately from the generator's reason extraction.
 if r['category']=='model_invocation': assert '"reason":"Model invocation failed:' in original['result']
 elif r['category']=='worker_outcome':
  result=json.loads(original['result'])
  assert result['retry_scope']=='worker'
  assert result['reason'] in ['Construction/qualification failed; artifacts preserved and worker deleted','Worker expired before durable upload']
  assert jobs[r['attempt']]['status']=='deleted'
 elif r['category']=='publication_reconciliation':
  assert original['stage']=='publish'
  assert json.loads(original['result'])['reason']=='Publication incomplete; retry reconciles destination files and tags'
 else:
  assert original['stage'] in ['discover','build']
  assert 'Model invocation failed:' not in original['result']
assert len({r['server_id'] for r in accounting['worker_retry_jobs']})==206
for r in accounting['worker_retry_jobs']: assert r['server_id']==jobs[r['attempt']]['server_id']
discovered={a['candidate'] for a in attempts if a['stage']=='discover' and a['status']=='done'}
cutoff_candidates=[]
for name in ['candidates_carry_in.json','candidates_new_admissions.json']:
 cutoff_candidates.extend(c for c in read('evidence/costs/2026-11-16/inputs/'+name) if c['id'] in discovered)
assert len(cutoff_candidates)==len({c['id'] for c in cutoff_candidates})==54
assert all(datetime.fromisoformat(c['updated'])<end for c in cutoff_candidates)
assert Counter(c['stage'] for c in cutoff_candidates)==accounting['discovery_completed_cutoff_states']=={
 'published':14,'deferred':37,'rejected':2,'build':1}
assert accounting['discovery_completed_candidates']==cutoff_candidates
built={a['candidate'] for a in attempts if a['stage']=='build' and a['status']=='done'}
deferred={c['id']:c for c in cutoff_candidates if c['stage']=='deferred'}
assert len(accounting['deferred_candidate_records'])==len(deferred)==37
assert {d['candidate'] for d in accounting['deferred_candidate_records']}==set(deferred)
assert sum(c not in built for c in deferred)==accounting['deferred_without_completed_build']==35
assert accounting['deferral_categories']=={'build_worker_failure_limit':31,'build_task_failure_limit':3,'semantic_repair_limit':2,'explicit_build_deferral':1}
assert Counter(d['category'] for d in accounting['deferred_candidate_records'])==accounting['deferral_categories']
for d in accounting['deferred_candidate_records']:
 assert d['completed_build']==(d['candidate'] in built)
 history=sorted((a for a in attempts if a['candidate']==d['candidate']),key=lambda a:a['started'])
 last=history[-1]
 assert d['last_attempt']==last['id'] and d['last_outcome']==last['status']
 if d['category'].startswith('build_'):
  assert last['status']=='retry' and last['stage']=='build'
  assert deferred[d['candidate']]['reason'].startswith('Attempt limit reached:')
  scope=json.loads(last['result']).get('retry_scope','task')
  assert d['category']=='build_'+scope+'_failure_limit'
  failures=[]
  for a in history:
   if a['stage']=='build' and a['status']=='retry':
    try: failure_scope=json.loads(a['result']).get('retry_scope','task')
    except json.JSONDecodeError:
     assert '[truncated ' in a['result']
     failure_scope='task'
    if failure_scope==scope: failures.append(a)
  assert len(failures)==5
 elif d['category']=='semantic_repair_limit':
  assert d['completed_build'] and last['status']=='repair' and last['stage']=='evaluate'
  assert deferred[d['candidate']]['reason'].startswith('Semantic repair limit reached:')
 else: assert not d['completed_build'] and last['status']=='defer' and last['stage']=='build'
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
assert 'unknown/missing phases in a window are excluded rather than labeled negative' in response['reason']
assert "for future in range(year + 1, year + 5):\n            if future in unknown_phase.get((key, agency), set()):\n                ambiguous = True\n                break\n        if ambiguous:\n            excluded['unknown_phase_in_window'] += 1\n            continue" in builder
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
for banned in ['presentation emphasis','we now focus','later paper','interim results','holdout AUC','BLOCKER.json','---','…']:
 assert banned.lower() not in tex.lower(), banned
citations=set()
for c in re.findall(r'\\cite\{([^}]+)\}',tex): citations.update(c.split(','))
assert len(citations)==17
assert 'identical-runs' in citations
performance=read('paper-agent27-short/analysis/consumer-results.json')
assert sha(ROOT/performance['snapshot'])==performance['snapshot_sha256']
assert sha(ROOT/performance['qualification_coverage'])==performance['qualification_coverage_sha256']
assert {r['dataset'] for r in performance['records']}==set(consumer)
evaluated_releases=[r for r in release['records'] if r['dataset'] in consumer]
assert [r['dataset'] for r in performance['records']]==[r['dataset'] for r in evaluated_releases]
for plotted, released in zip(performance['records'],evaluated_releases,strict=True):
 assert plotted['label']==released['short_name']==released['label'].split(' (')[0]
assert 'ranges of absolute scores overlapped' not in tex
assert 'Task (domain) & Consumer' not in tex
for r in performance['records']:
 assert sha(ROOT/r['summary'])==r['summary_sha256']
 summary=read(r['summary'])
 baseline=[s for s in summary['scores'] if s['kind']=='ordinary']
 agents={s['id']:s['holdout_auc'] for s in summary['scores'] if s['kind']=='agent'}
 assert len(baseline)==1 and len(agents)==3
 assert r['consumer_scores']==agents and r['baseline_auc']==baseline[0]['holdout_auc']
 tuned={s['id']:s['holdout_auc'] for s in summary['scores'] if s['kind']=='random'}
 assert len(tuned)==3 and set(tuned)=={k+'--random' for k in agents}
 assert r['tuned_scores']==tuned
 assert r['tuned_median']==statistics.median(tuned.values())
 assert r['tuned_min']==min(tuned.values()) and r['tuned_max']==max(tuned.values())
 assert r['consumer_median']==statistics.median(agents.values())
 assert r['consumer_min']==min(agents.values()) and r['consumer_max']==max(agents.values())
 assert r['all_three_above_baseline']==(min(agents.values())>r['baseline_auc'])
 assert sha(ROOT/r['qualification_receipt'])==r['qualification_receipt_sha256']
 assert read(r['qualification_receipt'])['accept_exit_code']==0
assert sum(r['all_three_above_baseline'] for r in performance['records'])==11
assert [round(v,3) for v in performance['median_auc_range']]==[.601,.913]
assert sum(abs(r['consumer_median']-r['tuned_median'])<.01 for r in performance['records'])==5
sbir=next(r for r in performance['records'] if r['dataset']=='sbir-phase1-to-phase2-conversion')
assert min(sbir['tuned_scores'].values())>max(sbir['consumer_scores'].values())
paired={r['dataset']:[v-r['tuned_scores'][k+'--random'] for k,v in r['consumer_scores'].items()] for r in performance['records']}
assert paired==performance['paired_comparisons']
assert sum(min(v)>0 for v in paired.values())==9
assert sum(min(v)<0<max(v) for v in paired.values())==2
assert sum(max(v)<0 for v in paired.values())==1
overlap={r['dataset'] for r in performance['records'] if max(r['consumer_min'],r['tuned_min'])<=min(r['consumer_max'],r['tuned_max'])}
assert overlap==set(performance['overlapping_run_ranges'])=={'t100-new-route-survival','sdwis-lcr-lead-action-level-next-period','caa-fce-hpv-escalation','faa-wildlife-strike-substantial-damage'}
gains=[r['consumer_median']-r['baseline_auc'] for r in performance['records'] if r['all_three_above_baseline']]
assert [round(min(gains),3),round(max(gains),3)]==[.008,.072]
report={'production_attempts':len(attempts),'milestones':milestones,'retry_counts':{'discovery':101,'build':260,'semantic_repair':21},
 'attempt_accounting_sha256':sha(OUT/'analysis/attempt-accounting.json'),
 'complete_attempt_outcomes':accounting['stage_outcomes'],
 'discovery_completed_cutoff_states':accounting['discovery_completed_cutoff_states'],
 'deferral_categories':accounting['deferral_categories'],
 'deferred_without_completed_build':accounting['deferred_without_completed_build'],
 'publications':14,'consumer_datasets':12,'scored_models_checked':sum(r['scored_models'] for r in consumer.values()),
 'consumer_summaries':consumer,'latency_min_max_median_minutes':[min(latencies),max(latencies),statistics.median(latencies)],
 'cost_range_usd':cost['factory_total_time_priced_usd_range'],'stage_costs_reconcile':True,'build_share_percent':stage['build_share_at_midpoint']*100,
 'sbir_original_files_verified':len(retrieval['sha256']),'first_release_trace_attempts':len(trace),'long_paper_files_preserved':len(preserved),'citations':sorted(citations),
 'disclosure_documents_checked':36,'disclosure_conditions':dict(condition_statuses),
 'disclosure_concerns':dict(concern_statuses),
 'disclosure_review_sha256':sha(OUT/'analysis/disclosure-review.json'),
 'manuscript_sha256':sha(OUT/'draft/main.tex'),
 'consumer_results_sha256':sha(OUT/'analysis/consumer-results.json'),
 'consumer_results_checked':len(performance['records']),
 'scope':'Recorded quantities, input identities, consumer completion, source-review identities and known wording checks. Does not mechanically establish semantic correctness of every sentence; manual claim and page reviews are separate.'}
(OUT/'analysis/record-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['publications','consumer_datasets','production_attempts','stage_costs_reconcile','long_paper_files_preserved']}))
