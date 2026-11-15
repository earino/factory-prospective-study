#!/usr/bin/env python3
"""Prospective study collector and bounded dispatcher. No production mutations."""
import argparse,datetime as dt,fcntl,gzip,hashlib,json,os,plistlib,re,shutil,signal,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import run_study as runner
P=json.loads((ROOT/'protocol.json').read_text())
LOCAL=ROOT/'.local'; LOCAL.mkdir(exist_ok=True)
E=ROOT/'evidence'; E.mkdir(exist_ok=True)
def now():return dt.datetime.now(dt.timezone.utc)
def parse(s):return dt.datetime.fromisoformat(s.replace('Z','+00:00'))
def read(p,default=None):return json.loads(p.read_text()) if p.exists() else default
def write(p,v):runner.write(p,v)
def fetch(url):
    with urllib.request.urlopen(url,timeout=60) as r:return r.read()
def git(args,cwd=ROOT):return runner.command(['git',*args],cwd=cwd,timeout=180).strip()
def checkpoint(message,push=True,paper=False):
    with (LOCAL/'git.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        git(['add','--','evidence','queue.json','STATUS.md'])
        if paper:git(['add','--','paper'])
        if subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode==1:git(['commit','-m',message])
        if push:
            git(['push','origin','HEAD']);runner.check_ci(ROOT,git(['rev-parse','HEAD']))
def eligible(snapshot):
    existing=set(read(ROOT/'baseline.json',{}).get('published_ids',[]))
    rows=snapshot['releases']['releases']
    return sorted([r for r in rows if r.get('workflow')=='modern' and r.get('published') and r['dataset'] not in existing and
                   parse(P['cohort_start'])<=parse(r['verified_at'])<=parse(P['cohort_close'])],key=lambda r:(r['verified_at'],r['dataset']))
def collect():
    raw=fetch(P['dashboard']);x=json.loads(raw);stamp=now().strftime('%Y%m%dT%H%M%SZ')
    (E/'snapshots').mkdir(exist_ok=True)
    (E/'snapshots'/f'{stamp}.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    if not (ROOT/'baseline.json').exists():
        raise RuntimeError('Register baseline before monitoring')
    q=read(ROOT/'queue.json',[]);known={r['dataset'] for r in q}
    for r in eligible(x):
        if r['dataset'] not in known:q.append(dict(dataset=r['dataset'],verified_at=r['verified_at'],release=r,status='queued'));known.add(r['dataset'])
    q.sort(key=lambda r:(r['verified_at'],r['dataset']))
    for i,r in enumerate(q):
        r['selected']=i<P['max_datasets']
        if not r['selected'] and r['status']=='queued':r['status']='capacity_excluded'
    write(ROOT/'queue.json',q)
    refresh_status(x,q)
    return q

def refresh_status(x,q):
    status={'observed_at':now().isoformat(),'snapshot_generated_at':x['generated_at'],'factory_counts':x['candidates']['counts'],
            'window':P,'queue':[{k:r.get(k) for k in ['dataset','verified_at','status','selected','branch','error']} for r in q],
            'consumer':read(LOCAL/'worker.json',{}),'paper':read(LOCAL/'paper.json',{}),
            'retries':[dict(execution_id=r['execution_id'],dataset=r['dataset'],
                           outcome=read(LOCAL/'outcomes'/f"{r['execution_id']}.json",{}))
                       for r in read(E/'retries/plan.json',{}).get('runs',[])]}
    write(E/'latest.json',status)
    (ROOT/'STATUS.md').write_text('# Prospective study status\n\n'+json.dumps(status,indent=2)+'\n')

def pin(r):
    name=r['dataset']
    if not re.fullmatch('[a-z0-9][a-z0-9-]+',name):raise ValueError('Unsafe dataset name')
    tag=r['release']['release_tag'];api=json.loads(fetch(f'https://huggingface.co/api/datasets/earino/factory-{name}/revision/{tag}'))
    revision=api['sha'];raw=fetch(f'https://huggingface.co/datasets/earino/factory-{name}/resolve/{revision}/MANIFEST.json');m=json.loads(raw)
    if (m['dataset'],m['version'])!=(name,tag):raise ValueError('Publication identity mismatch')
    return [name,tag,revision,hashlib.sha256(raw).hexdigest()]

def bounded_agent(work,prompt,seconds,output):
    work.mkdir(parents=True,exist_ok=True);(work/'mcp.json').write_text('{"mcpServers":{}}\n')
    argv=['claude','-p',prompt,'--model',P['model'],'--effort','high','--output-format','stream-json','--verbose',
          '--safe-mode','--setting-sources','','--strict-mcp-config','--mcp-config',str(work/'mcp.json'),
          '--disable-slash-commands','--permission-mode','dontAsk','--permission-prompts','none',
          '--tools','Bash,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch','--allowedTools','Bash,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch','--no-chrome']
    try:
        runner.command(argv,cwd=work,timeout=seconds,env=runner.clean_env(5),output=output)
        return {'ok':True,'summary':runner.cli_summary(output)}
    except Exception as e:return {'ok':False,'error':str(e)[-1200:],'summary':runner.cli_summary(output) if output.exists() else {}}

def archive_trace(source,dest):
    if not source.exists():return
    dest.parent.mkdir(parents=True,exist_ok=True)
    with source.open(errors='replace') as src,gzip.open(dest,'wt') as out:
        for line in src:out.write(runner.redact(line))
    write(dest.with_suffix('.provenance.json'),{'raw_sha256':runner.sha(source),'archive_sha256':runner.sha(dest),'redaction':'runner credential-pattern and environment-secret redaction; raw retained locally'})

def execution_id(r):
    value=r.get('execution_id',r['dataset'])
    if not re.fullmatch('[a-z0-9][a-z0-9-]+',value):raise ValueError('Unsafe execution ID')
    return value

def execute(r):
    name=r['dataset'];identity=execution_id(r)
    work=LOCAL/'studies'/identity;work.mkdir(parents=True,exist_ok=True)
    if not (work/'releases.json').exists():
        for n in ['run_study.py','agent.md']:shutil.copyfile(ROOT/n,work/n)
        entry=r.get('pinned_release') or pin(r)
        if entry[0]!=name or entry[1]!=r['release']['release_tag']:raise ValueError('Retry pin identity mismatch')
        write(work/'releases.json',[entry]);git(['init','-b','main'],work);runner.ensure_repo(work)
        git(['branch','-m','consumer/'+identity],work);git(['remote','add','origin',P['remote']],work)
        # Public predictor contract review happens before any holdout data is obtained.
        runner.prepare_dataset(work,entry)
        review=LOCAL/'reviews'/identity;review.mkdir(parents=True,exist_ok=True)
        prompt=(ROOT/'prompts/pre-review.md').read_text().replace('{STUDY}',str(work))
        result=bounded_agent(review,prompt,900,review/'pre-review.jsonl')
        dest=E/'reviews'/identity;dest.mkdir(parents=True,exist_ok=True)
        write(dest/'pre-review-invocation.json',result)
        archive_trace(review/'pre-review.jsonl',dest/'pre-review.jsonl.gz')
        for f in ['PRE-REVIEW.md','cluster.json']:
            if (review/f).exists():shutil.copyfile(review/f,dest/f)
        write(dest/'pinned-release.json',entry)
        checkpoint('Pin release and record prescoring contract review: '+identity)
    deadline=min(parse(P['research_stop']).timestamp(),time.time()+P['per_dataset_wall_hours']*3600)
    log=LOCAL/'logs'/f'{identity}.log';log.parent.mkdir(exist_ok=True)
    argv=[sys.executable,work/'run_study.py','run','--model',P['model'],'--jobs',str(P['jobs']),'--threads',str(P['threads']),'--push']
    with log.open('ab') as out:
        proc=subprocess.Popen(argv,cwd=work,env=runner.clean_env(5),stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            code=proc.wait(timeout=max(1,deadline-time.time()))
        except subprocess.TimeoutExpired:
            # Let the runner stop its separately owned Claude/experiment groups and save state.
            proc.send_signal(signal.SIGINT)
            try:proc.wait(timeout=120)
            except subprocess.TimeoutExpired:runner.stop_group(proc.pid)
            raise TimeoutError('Registered study wall-time or global deadline reached; preserved as incomplete')
        if code:raise RuntimeError(f'Consumer runner exited {code}; see {log}')
    runner.command([sys.executable,work/'run_study.py','verify'],cwd=work,timeout=120)
    out=E/'consumer'/identity;out.mkdir(parents=True,exist_ok=True)
    for src in ['study.json','results/summary.json','results/scores.csv','results/REPORT.md','evidence/COMPLETED.json','evidence/INTEGRITY.json']:
        f=work/src
        if f.exists():
            d=out/src;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
    # Derived checks run after the per-dataset holdout barrier; originals stay sealed.
    review_out=E/'reviews'/identity/'post';review_out.mkdir(parents=True,exist_ok=True)
    env=runner.clean_env(5);env.update(STUDY_ROOT=str(work),REVIEW_OUT=str(review_out),CLUSTER_FILE=str(E/'reviews'/identity/'cluster.json'))
    checks=[]
    for tool in ['review_checks.py','probe_all_training_features.py','probe_artifacts.py','bootstrap.py']:
        try:
            runner.command([work/'.study/venv/bin/python',ROOT/'review_tools'/tool],cwd=ROOT,timeout=900,env=env,output=LOCAL/'logs'/f'{identity}-{tool}.log')
            checks.append({'tool':tool,'ok':True})
        except Exception as e:checks.append({'tool':tool,'ok':False,'error':str(e)[-1200:]})
    write(review_out/'execution.json',checks)
    return git(['rev-parse','HEAD'],work)

def pending_work():
    retries=read(E/'retries/plan.json',{}).get('runs',[])
    regular=[r for r in read(ROOT/'queue.json',[]) if r.get('selected')]
    return [r for r in retries+regular if not (LOCAL/'outcomes'/f'{execution_id(r)}.json').exists()]

def work_queue():
    with (LOCAL/'consumer.lock').open('w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return
        while now()<parse(P['research_stop']):
            # Queue writer is the monitor; this worker communicates via per-dataset result files.
            choices=pending_work()
            if not choices:return
            r=choices[0];name=r['dataset'];identity=execution_id(r)
            write(LOCAL/'worker.json',{'dataset':name,'execution_id':identity,'started':now().isoformat(),'status':'running'})
            result={'dataset':name,'execution_id':identity,'branch':'consumer/'+identity,'started':now().isoformat()}
            try:result.update(status='complete',commit=execute(r))
            except Exception as e:result.update(status='incomplete',error=str(e)[-2000:])
            result['finished']=now().isoformat();write(LOCAL/'outcomes'/f'{identity}.json',result);write(E/'outcomes'/f'{identity}.json',result)
            write(LOCAL/'worker.json',result)
            # Evidence is copied by monitor under its Git lock, avoiding concurrent main commits.

def retire_monitor():
    """Archive only this study's schedules, then unload them. Evidence stays intact."""
    base='org.earino.factory-prospective-study'
    folder=Path.home()/'Library/LaunchAgents'
    owned=[]
    for label in [base+'.awake',base]:
        path=folder/(label+'.plist')
        if path.exists():
            spec=plistlib.loads(path.read_bytes())
            if (path.is_symlink() or spec.get('Label')!=label or
                spec.get('WorkingDirectory')!=str(ROOT) or
                spec.get('ProgramArguments',[None,None])[1:]!=[str(ROOT/'controller.py'),'awake' if label.endswith('.awake') else 'tick']):
                raise RuntimeError('Refusing to remove an unrecognized schedule: '+str(path))
            owned.append((label,path))
    archive=LOCAL/'retired-launchagents';archive.mkdir(exist_ok=True)
    for label,path in owned:
        target=archive/path.name
        if target.exists() and target.read_bytes()!=path.read_bytes():
            raise RuntimeError('Retired schedule differs; preserve both for inspection')
        path.replace(target)
    write(E/'monitor-stop.json',{'at':now().isoformat(),'reason':'registered window ended',
          'schedules_archived':[label for label,path in owned],'evidence_preserved':True,
          'note':'Plists removed before unloading; no reload on next login. Self-unload ends this process.'})
    # Self is last: launchd can terminate this process when that job is unloaded.
    for label in [base+'.awake',base]:
        subprocess.run(['launchctl','bootout',f'gui/{os.getuid()}/'+label],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def tick():
    with (LOCAL/'monitor.lock').open('w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return
        if now()>=parse(P['paper_ready_due'])+dt.timedelta(hours=1):
            retire_monitor();return
        last=read(LOCAL/'last-collect.json',{})
        if time.time()-last.get('epoch',0)>=P['poll_seconds']:
            q=collect()
            for r in q:
                result=read(LOCAL/'outcomes'/f"{r['dataset']}.json")
                if result:r.update(result)
                elif r.get('selected') and now()>=parse(P['research_stop']):r['status']='incomplete_at_deadline'
            write(ROOT/'queue.json',q);write(LOCAL/'last-collect.json',{'epoch':time.time()})
            latest=read(E/'latest.json');latest['queue']=[{k:r.get(k) for k in ['dataset','verified_at','status','selected','branch','error']} for r in q]
            write(E/'latest.json',latest);(ROOT/'STATUS.md').write_text('# Prospective study status\n\n'+json.dumps(latest,indent=2)+'\n')
            checkpoint('Record prospective factory observation '+now().strftime('%Y-%m-%d %H:%M'),push=True)
        if now()<parse(P['research_stop']):
            spawn('work')
        if now()>=parse(P['analysis_start']):spawn('paper')

def spawn(action):
    (LOCAL/'logs').mkdir(exist_ok=True)
    with (LOCAL/'logs'/f'{action}-launcher.log').open('ab') as f:
        subprocess.Popen([sys.executable,__file__,action],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=runner.clean_env(1))

def paper():
    with (LOCAL/'paper.lock').open('w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return
        state=read(LOCAL/'paper.json',{})
        if state.get('attempts',0)>=2 or state.get('status')=='draft_produced':return
        if now()>parse(P['paper_ready_due']):return
        # Ensure no consumer process owns its lock before analysis receives holdout results.
        with (LOCAL/'consumer.lock').open('a') as c:
            try:fcntl.flock(c,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:return
            work=ROOT/'paper';work.mkdir(exist_ok=True)
            prompt=(ROOT/'prompts/paper.md').read_text().replace('{ROOT}',str(ROOT))
            seconds=min(3*3600,max(1,parse(P['paper_ready_due']).timestamp()-time.time()))
            result=bounded_agent(work,prompt,seconds,LOCAL/'logs'/f'paper-{state.get("attempts",0)}.jsonl')
            complete=(work/'output/paper.pdf').exists() and (work/'SIGNOFF.md').exists()
            write(LOCAL/'paper.json',{'attempts':state.get('attempts',0)+1,'status':'draft_produced' if complete else 'incomplete','result':result,'at':now().isoformat()})
            write(E/'paper-run.json',read(LOCAL/'paper.json'))
            archive_trace(LOCAL/'logs'/f'paper-{state.get("attempts",0)}.jsonl',E/'paper-transcripts'/f'paper-{state.get("attempts",0)}.jsonl.gz')
            checkpoint('Preserve bounded paper preparation output',paper=True)

def awake():
    seconds=int((parse(P['paper_ready_due'])+dt.timedelta(hours=1)-now()).total_seconds())
    if seconds>0:subprocess.run(['/usr/bin/caffeinate','-i','-t',str(seconds)],check=True)

def main():
    a=argparse.ArgumentParser();a.add_argument('action',choices=['collect','tick','work','paper','status','awake']);args=a.parse_args()
    if args.action=='collect':collect()
    elif args.action=='tick':tick()
    elif args.action=='work':work_queue()
    elif args.action=='paper':paper()
    elif args.action=='awake':awake()
    else:print(json.dumps(read(E/'latest.json',{}),indent=2))
if __name__=='__main__':main()
