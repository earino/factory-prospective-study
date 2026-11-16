"""Attribute the frozen operating estimate to recorded stages, then plot it."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'paper-agent27-short'
base=ROOT/'evidence/costs/2026-11-16'
summary=json.loads((base/'summary.json').read_text())
workers=json.loads((base/'factory-worker-costs.json').read_text())
fx=summary['workers']['usd']/summary['workers']['eur']
rows={s:{'inference_low_usd':0.,'inference_high_usd':0.,'worker_usd':0.,'hosting_usd':0.,'workers':0} for s in ['discover','build','evaluate','publish','hosting']}
for w in workers:
 rows[w['stage']]['worker_usd']+=w['cost_eur']*fx
 rows[w['stage']]['workers']+=1
for s,r in summary['model_by_stage'].items():
 rows[s]['inference_low_usd']=r['time_priced_low_usd']
 rows[s]['inference_high_usd']=r['time_priced_high_usd']
rows['hosting']['hosting_usd']=summary['hosting_usd']
for s,r in rows.items():
 r['total_low_usd']=r['inference_low_usd']+r['worker_usd']+r['hosting_usd']
 r['total_high_usd']=r['inference_high_usd']+r['worker_usd']+r['hosting_usd']
 r['midpoint_usd']=(r['total_low_usd']+r['total_high_usd'])/2
low=sum(r['total_low_usd'] for r in rows.values()); high=sum(r['total_high_usd'] for r in rows.values())
assert abs(low-summary['factory_total_time_priced_usd_range'][0])<1e-8
assert abs(high-summary['factory_total_time_priced_usd_range'][1])<1e-8
report={'sources':{str((base/n).relative_to(ROOT)):hashlib.sha256((base/n).read_bytes()).hexdigest() for n in ['summary.json','factory-worker-costs.json']},
 'usd_per_eur':fx,'scope':'Same recorded recurring-cost estimate and window as the original calculation; attribution follows recorded model and worker stages. Build includes construction, checks and baseline fitting. Hosting remains shared. No cost is assigned from retry counts.',
 'stages':rows,'total_range_usd':[low,high],
 'build_share_at_midpoint':rows['build']['midpoint_usd']/((low+high)/2)}
(OUT/'analysis/stage-costs.json').write_text(json.dumps(report,indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'font.size':8})
fig,ax=plt.subplots(figsize=(3.48,1.65))
fig.subplots_adjust(left=.35,right=.93,top=.80,bottom=.25)
labels=['Discovery','Construction','Semantic review','Publication','Shared hosting']
for i,(stage,r) in enumerate(rows.items()):
 left=0
 for amount,color in [((r['inference_low_usd']+r['inference_high_usd'])/2,'#286f98'),(r['worker_usd'],'#16877c'),(r['hosting_usd'],'#8d99a5')]:
  if amount:
   ax.barh(i,amount,left=left,height=.62,color=color)
   if stage=='build': ax.text(left+amount/2,i,f'${amount:.2f}',ha='center',va='center',fontsize=8,color='white')
  left+=amount
 ax.text(left+.45,i,f'${left:.2f}',va='center',fontsize=8,color='#243746')
ax.set_yticks(range(5),labels); ax.invert_yaxis(); ax.set_xlim(0,29)
ax.set_xticks([0,10,20]); ax.set_xlabel('Estimated recurring expenditure (USD)',fontsize=8,labelpad=5)
ax.tick_params(axis='y',length=0,pad=6); ax.tick_params(axis='x',length=2,color='#aab6bd')
for side in ['top','right','left']: ax.spines[side].set_visible(False)
ax.spines['bottom'].set_color('#aab6bd'); ax.set_axisbelow(True); ax.grid(axis='x',color='#e5e9ed',lw=.6)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color='#286f98',label='Inference'),Patch(color='#16877c',label='Workers'),Patch(color='#8d99a5',label='Hosting')],loc='upper center',ncol=3,frameon=False,fontsize=8,bbox_to_anchor=(.54,1),handlelength=1,columnspacing=1.3)
fig.savefig(OUT/'draft/figures/stage-costs.pdf',metadata={'CreationDate':None,'ModDate':None})
print(json.dumps({'total_midpoint':(low+high)/2,'build_share':report['build_share_at_midpoint']}))
