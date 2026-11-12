import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import controller as c
class Tests(unittest.TestCase):
 def test_cohort_uses_fixed_window_and_does_not_select_by_scores(self):
  start=c.P['cohort_start'];end=c.P['cohort_close']
  def row(ds,t,score):return dict(dataset=ds,workflow='modern',published=True,verified_at=t,baseline_auc=score)
  x={'releases':{'releases':[row('b',start,.99),row('a',start,.1),row('too-late','2026-11-19T00:00:00Z',.99),row('old','2026-11-11T00:00:00Z',.99)]}}
  with patch.object(c,'read',return_value={'published_ids':['b']}):
   self.assertEqual([r['dataset'] for r in c.eligible(x)],['a'])
 def test_pins_manifest_identity(self):
  r={'dataset':'new-task','release':{'release_tag':'v1'}}
  with patch.object(c,'fetch',side_effect=[b'{"sha":"abc"}',b'{"dataset":"other","version":"v1"}']):
   with self.assertRaises(ValueError):c.pin(r)
 def test_runner_has_consistent_predictor_filter(self):
  import ast
  tree=ast.parse(c.runner.ENGINE)
  fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='drop_columns')
  code=compile(ast.Module(body=[fn],type_ignores=[]),'<contract>','exec');ns={'json':json};exec(code,ns)
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=root/'release/reproduction/construction.json';p.parent.mkdir(parents=True)
   p.write_text(json.dumps({'quality':{'features':['good','id','carry','label'],'id_columns':['id'],'carry_columns':['carry']}}))
   self.assertEqual(ns['drop_columns'](root/'release',{'target':'label'},['good','id','carry','label','extra']),['id','carry','label','extra'])
   with self.assertRaises(ValueError):ns['drop_columns'](root/'release',{'target':'label'},['id','carry','label'])
if __name__=='__main__':unittest.main()
