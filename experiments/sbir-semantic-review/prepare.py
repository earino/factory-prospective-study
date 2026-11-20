"""Freeze the two cases and three packet conditions. Never executes a model."""
import copy, difflib, hashlib, json, random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SRC=ROOT/'paper/analysis/final-2026-11-16/sbir-acceptance'
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 if (OUT/'inputs/manifest.json').exists():raise SystemExit('Inputs already frozen; refusing overwrite')
 prompt=(SRC/'evaluate-1/prompt.txt').read_text();idx=prompt.index('{"construction_code":')
 instructions=prompt[:idx];packet=json.loads(prompt[idx:]);desc=json.loads((SRC/'published-construction.json').read_text())
 manifest=json.loads((SRC/'published-manifest.json').read_text())
 builder=packet['construction_code']
 assert digest(builder.encode())==manifest['assets']['reproduction/build.py']['sha256']
 assert digest((SRC/'published-construction.json').read_bytes())==manifest['assets']['reproduction/construction.json']['sha256']
 assert packet['measurement']['qualification']['ok']
 assert all(x['passed'] for x in packet['measurement']['source-checks.json']['checks'])
 assert 'no outcome field is used to select rows' not in prompt
 originals=['evaluate-1/prompt.txt','evaluate-1/response.json','evaluate-1/response.txt','evaluate-1/usage.json','evaluate-1/attempt.json','evaluate-1/transcript.json','build-3/response.json','build-3/quality.json','published-construction.json','published-manifest.json','retrieval.json','manifest.json','checks.json','deployed-code.json']
 for name in originals:
  dst=OUT/'inputs/historical'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((SRC/name).read_bytes())
 (OUT/'inputs/build.py').write_text(builder)
 consistent=copy.deepcopy(desc)
 selection=('One row per resolvable firm key (UEI, else DUNS, else normalized company name plus state), restricted to firms whose earliest award year is 2005 through 2018 and whose records in that earliest year all have Phase I. The four-year outcome window must end by the maximum award year in the frozen file. Exclude a firm if any of its records has an unparseable award year, any Phase II record has a missing agency, or any unknown/missing-phase record has a missing agency. Among candidate index Phase I records, require a unique earliest proposal_award_date when there are multiple records in the earliest year, and require a nonempty index agency. Also exclude the firm if an unknown/missing-phase record from that same agency occurs in years y+1 through y+4. These exclusions use the full current-vintage file, including later records and outcome-window phase information. The population is therefore conditional on this recorded label ascertainment, not an unconditional population identifiable at the index award date.')
 old=desc['quality']['task'];q=consistent['quality'];q['timing']['row_selection']['rule']=selection
 q['task']['population']=selection
 q['task']['target']=old['target']+' Apply all population exclusions before assigning either label; later unknown/missing-phase records can exclude a firm even if a Phase II record exists.'
 q['task']['prediction_time']=old['prediction_time'].replace('Only fields on the index Phase I award record are read.','Only predictor features come from the index Phase I award record; population selection and labels use later records as declared in the population rule.')
 q['evaluation_contract']['selection']={'kind':'outcome_conditioned','evidence':selection}
 q['evaluation_contract']['limitations'].append('The selected population is conditioned on later record completeness and phase/agency information; it is not the unrestricted award-time population.')
 # Update the same declared task/contract wherever it appears in the original packet.
 cp=copy.deepcopy(packet)
 for key in ['population','target','prediction_time']:
  cp['source']['task'][key]=q['task'][key]
 cp['measurement']['evaluation_contract']=copy.deepcopy(q['evaluation_contract'])
 # Preserve builder, source-check reports, and baseline/qualification measurements exactly.
 assert cp['construction_code']==packet['construction_code']
 for key in packet['measurement']:
  if key!='evaluation_contract':assert cp['measurement'][key]==packet['measurement'][key]
 dump(OUT/'inputs/cases/original-descriptor.json',desc)
 dump(OUT/'inputs/cases/consistent-descriptor.json',consistent)
 dump(OUT/'inputs/cases/original-packet.json',packet)
 dump(OUT/'inputs/cases/consistent-packet.json',cp)
 for name,a,b in [('descriptor',desc,consistent),('packet',packet,cp)]:
  (OUT/f'inputs/{name}.diff').write_text(''.join(difflib.unified_diff(json.dumps(a,indent=2,ensure_ascii=False).splitlines(True),json.dumps(b,indent=2,ensure_ascii=False).splitlines(True),fromfile='original',tofile='consistent')))
 extra=('Before deciding, enumerate the conditions in the construction code that include or exclude rows. Compare each condition with the declared population and selection rules in the supplied descriptor. For any disagreement, cite the relevant declaration and code and explain the conflict. Distinguish a contradiction between declaration and implementation from a limitation that the declaration already states. Include unresolved material disagreements in findings; record completed reconciliation in reason or limitations.\n')
 runs=[]
 for case,p,d in [('original',packet,desc),('consistent',cp,consistent)]:
  for condition in ['original_packet','complete_packet','explicit_comparison']:
   payload=copy.deepcopy(p)
   if condition!='original_packet':payload['published_descriptor']=d
   text=instructions+(extra if condition=='explicit_comparison' else '')+json.dumps(payload,sort_keys=True)
   if case=='original' and condition=='original_packet':text=prompt
   dest=OUT/f'inputs/prompts/{case}--{condition}.txt';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
   for repetition in range(1,6):runs.append({'case':case,'condition':condition,'repetition':repetition,'prompt':str(dest.relative_to(OUT))})
 random.Random(20261120).shuffle(runs)
 for i,r in enumerate(runs,1):r['run_id']=f'r{i:02d}'
 dump(OUT/'schedule.json',{'seed':20261120,'runs':runs})
 files={str(p.relative_to(OUT)):digest(p.read_bytes()) for p in sorted((OUT/'inputs').rglob('*')) if p.is_file()}
 manuscript={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted((ROOT/'paper-agent27-short').rglob('*')) if p.is_file() and (p.suffix in ['.tex','.pdf','.bib'] or p.name=='paper-source.zip')}
 dump(OUT/'inputs/manifest.json',{'source_repository':'earino/factory-prospective-study','release_version':manifest['version'],'historical_attempt':'rw-9f58fbd0fa13-evaluate-1','files':files,'submitted_artifact_hashes':manuscript,'builder_sha256':digest(builder.encode()),'historical_prompt_exact':True,'comparison_case':'Constructed declaration consistent with the inspected selection filters; not a valid-task certification.'})
 print('Frozen',len(files),'input files;',len(runs),'planned reviews')
if __name__=='__main__':main()
