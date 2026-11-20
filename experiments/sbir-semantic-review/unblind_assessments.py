"""Join fixed blind content observations with case identity, preserving both."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
if __name__=='__main__':
 out=BASE/'assessment';source=read(out/'blind-observations.json');mapping=read(out/'mapping.json');schedule={r['run_id']:r for r in read(BASE/'schedule.json')['runs']};rows=[]
 for r in source['rows']:
  for field in ['target_conflict_alleged','partial_selection_finding','declared_selection_acknowledged','verdict','ambiguous']:assert r[field] is not None,(r['blind_id'],field)
  run=schedule[mapping[r['blind_id']]]
  rows.append({**r,'full_detection':bool(r['target_conflict_alleged'] and run['case']=='original'),'false_contradiction':bool(r['target_conflict_alleged'] and run['case']=='consistent')})
 target=out/'assessments.json'
 if target.exists():raise SystemExit('Refusing to overwrite final assessments')
 target.write_text(json.dumps({'assessor':source['assessor'],'method':'Initial target-conflict allegations from blind-observations.json joined with frozen case identity. Other concerns do not count as false contradiction reports.','rows':rows},indent=2)+'\n')
 print('Joined',len(rows),'assessments to case identity')
