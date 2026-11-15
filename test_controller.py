import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import controller as c
class Tests(unittest.TestCase):
 def test_retry_does_not_reopen_or_overwrite_original_outcome(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);local=root/'local';e=root/'evidence';(local/'outcomes').mkdir(parents=True);(e/'retries').mkdir(parents=True)
   original=local/'outcomes/task.json';original.write_text('{"status":"complete"}')
   (root/'queue.json').write_text(json.dumps([{'dataset':'task','selected':True},{'dataset':'next','selected':True}]))
   (e/'retries/plan.json').write_text(json.dumps({'runs':[{'dataset':'task','execution_id':'task-retry-1'}]}))
   with patch.object(c,'ROOT',root),patch.object(c,'LOCAL',local),patch.object(c,'E',e):
    self.assertEqual([c.execution_id(x) for x in c.pending_work()],['task-retry-1','next'])
    (local/'outcomes/task-retry-1.json').write_text('{"status":"complete"}')
    self.assertEqual([c.execution_id(x) for x in c.pending_work()],['next'])
   self.assertEqual(original.read_text(),'{"status":"complete"}')
 def test_retry_identity_rejects_path_escape(self):
  with self.assertRaisesRegex(ValueError,'Unsafe execution ID'):
   c.execution_id({'dataset':'task','execution_id':'../task'})
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
 def test_expired_tick_does_no_work(self):
  with patch.object(c,'now',return_value=c.parse(c.P['paper_ready_due'])+c.dt.timedelta(hours=2)),patch.object(c,'retire_monitor') as retire,patch.object(c,'collect') as collect,patch.object(c,'spawn') as spawn:
   c.tick();retire.assert_called_once();collect.assert_not_called();spawn.assert_not_called()
 def test_retirement_preserves_evidence_and_removes_only_owned_schedules(self):
  with tempfile.TemporaryDirectory() as d:
   home=Path(d);folder=home/'Library/LaunchAgents';folder.mkdir(parents=True);local=home/'local';local.mkdir();e=home/'evidence';e.mkdir();(e/'keep').write_text('keep')
   base='org.earino.factory-prospective-study'
   for suffix,action in [('', 'tick'),('.awake','awake')]:
    label=base+suffix;(folder/(label+'.plist')).write_bytes(c.plistlib.dumps({'Label':label,'WorkingDirectory':str(c.ROOT),'ProgramArguments':['python',str(c.ROOT/'controller.py'),action]}))
   (folder/'unrelated.plist').write_text('unrelated')
   with patch.object(Path,'home',return_value=home),patch.object(c,'LOCAL',local),patch.object(c,'E',e),patch.object(c.subprocess,'run') as run:
    c.retire_monitor()
    self.assertEqual(run.call_count,2)
   self.assertEqual((e/'keep').read_text(),'keep');self.assertTrue((folder/'unrelated.plist').exists());self.assertFalse((folder/(base+'.plist')).exists());self.assertTrue((local/'retired-launchagents'/(base+'.plist')).exists())
 def test_resume_rejects_changed_release_list(self):
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for name in ['run_study.py','agent.md','releases.json']:(root/name).write_text('original')
   protocol={'runner_sha256':c.runner.sha(root/'run_study.py'),'agent_sha256':c.runner.sha(root/'agent.md'),'release_list_sha256':c.runner.sha(root/'releases.json')}
   c.runner.write(root/'study.json',protocol)
   self.assertEqual(c.runner.register(root,SimpleNamespace()),protocol)
   (root/'releases.json').write_text('changed')
   with self.assertRaisesRegex(ValueError,'release list changed'):c.runner.register(root,SimpleNamespace())
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
