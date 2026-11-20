"""Create a reproducible shuffled response view without condition labels."""
import hashlib,json,random
from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 schedule=json.loads((BASE/'schedule.json').read_text())['runs']
 assert all((BASE/'runs'/r['run_id']/'finished.json').exists() for r in schedule),'Wait for all 30 runs'
 order=[r['run_id'] for r in schedule];random.Random(892734).shuffle(order)
 mapping={f'b{i:02d}':run for i,run in enumerate(order,1)}
 out=BASE/'assessment';out.mkdir(exist_ok=True)
 (out/'mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
 rows=[]
 for blind,run in mapping.items():
  p=BASE/'runs'/run/'response.txt'
  text=p.read_text() if p.exists() else '[No final response retained]'
  (out/f'{blind}.txt').write_text(text)
  rows.append({'blind_id':blind,'response_sha256':hashlib.sha256(text.encode()).hexdigest(),'target_conflict_alleged':None,'partial_selection_finding':None,'declared_selection_acknowledged':None,'verdict':None,'ambiguous':None,'supporting_excerpts':[],'other_concerns':[],'assessment_note':''})
 target=out/'blind-observations.json'
 if target.exists():raise SystemExit('Refusing to overwrite assessments')
 target.write_text(json.dumps({'assessor':'Codex, same investigator who prepared the protocol; condition labels hidden during initial assessment, content may reveal cases','stage':'Initial content assessment; case truth joined later to distinguish detection from false allegation','rows':rows},indent=2)+'\n')
 print('Created',len(rows),'shuffled response files and assessment template')
