"""Regenerate draft tables/figures from the captured compact evidence; no model fits."""
import collections,datetime,json,statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
P=Path(__file__).resolve().parents[1]; D=json.loads((P/'analysis/draft-inputs.json').read_text())['data']
C=D['evidence/costs/2026-11-15/summary.json']; cohort=D['evidence/costs/2026-11-15/inputs/cohort.json']
figdir=P/'draft/figures'; gen=P/'draft/generated'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#243342','text.color':'#243342','axes.edgecolor':'#9ba6ad','xtick.color':'#53616b','ytick.color':'#53616b','savefig.bbox':'tight'})
blue='#24658a'; teal='#16867b'; gold='#c78c2d'; grey='#a8b4be'
labels=['Civil trials','Utility reliability','Pipeline penalties','Device recalls','Airline routes','Research grants','Air enforcement','Wastewater','Wildlife strikes','Building permits','Railway hazmat']
names={r['dataset']:s for r,s in zip(cohort,labels)}
# Workflow figure, whose labels describe implementation rather than measurements.
fig,ax=plt.subplots(figsize=(7.0,2.0));ax.set_xlim(0,10);ax.set_ylim(0,3);ax.axis('off')
for i,(title,body) in enumerate([('Discover','Source + task\nEvidence + rights'),('Build','Generated code\nWorker checks'),('Evaluate','Bounded semantic\nreview + repair'),('Publish','Manifest + tags\nAnonymous reads')]):
 x=i*2.5;ax.add_patch(FancyBboxPatch((x+.08,1.38),2.15,1.1,boxstyle='round,pad=.06',facecolor='#eef4f7',edgecolor=blue,lw=.8));ax.text(x+1.155,2.18,title,ha='center',weight='bold',color=blue);ax.text(x+1.155,1.75,body,ha='center',va='center',fontsize=8)
 if i<3:ax.annotate('',xy=(x+2.58,1.93),xytext=(x+2.25,1.93),arrowprops=dict(arrowstyle='->',color=blue,lw=1))
ax.text(5,2.85,'Production: bounded model judgment; deterministic state, retries, workers and transfer',ha='center',fontsize=8)
ax.plot([.15,9.8],[1.09,1.09],color=grey,lw=.7)
ax.text(.1,.62,'Independent consumers',weight='bold',color=teal);ax.text(3.1,.62,'Pin release  →  3 research runs + controls  →  Freeze  →  Holdout + review',fontsize=8)
ax.text(.1,.08,'No consumer-result feedback to production during the observation window',fontsize=7.5,color='#53616b')
fig.savefig(figdir/'workflow.pdf');plt.close(fig)
# Cost and repeat workload; retries are stage attempts, never source rejection counts.
A=sum([D[f'evidence/costs/2026-11-15/inputs/attempts_{s}.json'] for s in ('carry_in','new_admissions')],[])
parse=datetime.datetime.fromisoformat; start=parse(C['window_start']); stop=parse(C['cutoff'])
A=[a for a in A if start<=parse(a['started'])<=stop]
counts=collections.Counter((a['stage'],a['status']) for a in A)
fig,(ax,bx)=plt.subplots(1,2,figsize=(7,2.65),gridspec_kw={'width_ratios':[1,1.35]})
vals=[sum(C['model_time_priced_usd_range'])/2,C['workers']['usd'],C['hosting_usd']]
ax.barh(['Inference','Workers','Hosting'],vals,color=[blue,teal,gold],height=.52);ax.invert_yaxis();ax.set_xlim(0,17);ax.set_xlabel('Estimated operating cost (USD)');ax.set_title(r'(a) \$27.84–\$27.94 across 11 releases',loc='left',fontsize=9)
for y,v in enumerate(vals):ax.text(v+.25,y,f'USD {v:.2f}',va='center',fontsize=8)
stages=['discover','build','evaluate','publish']; left=[0]*4
for group,color in [(['done'],teal),(['retry','repair'],gold),(['defer','reject'],grey),(['running'],blue)]:
 v=[sum(counts[s,k] for k in group) for s in stages];bx.barh(stages,v,left=left,color=color,height=.55,label={'done':'Done','retry':'Retry / repair','defer':'Defer / reject','running':'Open'}[group[0]]);left=[a+b for a,b in zip(left,v)]
bx.invert_yaxis();bx.set_xlabel('Recorded stage attempts started in window');bx.set_title(f'(b) {len(A)} attempts, including repeated work',loc='left',fontsize=9);bx.legend(ncol=2,frameon=False,fontsize=7,loc='lower right');bx.set_xlim(0,max(left)*1.16)
for y,v in enumerate(left):bx.text(v+2,y,str(v),va='center',fontsize=8)
fig.tight_layout(w_pad=2);fig.savefig(figdir/'operations.pdf');plt.close(fig)
# All available paired intervals, no best-run selection.
fig,axes=plt.subplots(2,3,figsize=(7,3.2),sharex=True)
with_ci=[r for r in cohort if (f"evidence/reviews/{r['dataset']}/post/bootstrap.json" in D and len(D[f"evidence/reviews/{r['dataset']}/post/bootstrap.json"]['comparisons']))]
for ax,r in zip(axes.flat,with_ci):
 ds=r['dataset']; b=D[f'evidence/reviews/{ds}/post/bootstrap.json']; rows=[c for c in b['comparisons'] if c['control'].endswith('--random')]
 ax.axvline(0,color=grey,lw=.9);ax.set_yticks([0,1,2],['Run 1','Run 2','Run 3']);ax.invert_yaxis()
 for i,c in enumerate(rows):ax.errorbar(c['delta'],i,xerr=[[c['delta']-c['low']],[c['high']-c['delta']]],fmt='o',color=blue,capsize=2,ms=3,lw=1)
 ax.set_title(f"{names[ds]} · {b['clusters']:,} groups",loc='left',fontsize=8);ax.set_xlim(-.085,.105);ax.set_xticks([-.05,0,.05,.10]);ax.grid(axis='x',alpha=.15)
for ax in axes[-1]:ax.set_xlabel('Holdout AUC difference')
fig.tight_layout(w_pad=1.4,h_pad=1.8);fig.savefig(figdir/'consumer-intervals.pdf');plt.close(fig)
# Tables are computed; paper interpretation is kept in the manuscript.
rows=[]; outcome_counts=collections.Counter(); probe_errors=[]; artifacts=0
for r in cohort:
 ds=r['dataset'];s=D[f'evidence/consumer/{ds}/results/summary.json'];outcome_counts.update(x['status'] for x in s['outcomes']); scores=s['scores']; ordinary=next(x['holdout_auc'] for x in scores if x['kind']=='ordinary'); agents=[x['holdout_auc'] for x in scores if x['kind']=='agent']; randoms=[x['holdout_auc'] for x in scores if x['kind']=='random']; n=next(x['holdout_rows'] for x in scores if x['kind']=='ordinary')
 b=D.get(f'evidence/reviews/{ds}/post/bootstrap.json');g=f"{b['clusters']:,}" if b and agents else ('?' if agents else '--')
 span=lambda v:f'{min(v):.3f}--{max(v):.3f}' if v else '--'
 rows.append(f"{names[ds]} & {n:,} & {ordinary:.3f} & {span(agents)} & {span(randoms)} & {g} \\")
 for p in D.get(f'evidence/reviews/{ds}/post/training-feature-probes.json',[]):
  if 'error' in p:probe_errors.append(p['run'])
 artifacts+=len(D.get(f'evidence/reviews/{ds}/post/artifact-probes.json',[]))
(gen/'score-rows.tex').write_text('\n'.join(line.rstrip(chr(92))+chr(92)*2 for line in rows)+'\n')
lat=[(parse(r['published_at'])-parse(r['created'])).total_seconds()/60 for r in cohort]
metrics={'stage_attempts':len(A),'stage_status_counts':{s:{k:counts[s,k] for k in ['done','retry','repair','defer','reject','running']} for s in stages},'unique_done_candidates':{s:len({a['candidate'] for a in A if a['stage']==s and a['status']=='done'}) for s in stages},'publication_latency_minutes':{'min':min(lat),'median':statistics.median(lat),'max':max(lat)},'original_consumer_outcomes':dict(outcome_counts),'artifact_probes':artifacts,'training_probe_errors':probe_errors,'cost':{'total':C['factory_total_time_priced_usd_range'],'per_release':C['factory_time_priced_usd_per_release_range']}}
(P/'analysis/derived.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))
