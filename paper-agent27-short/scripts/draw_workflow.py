from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

out=Path(__file__).resolve().parents[1]/'draft/figures/workflow.pdf'
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(7.15,2.1))
fig.subplots_adjust(0.005,0.01,0.995,0.99)
ax.set_xlim(0,7.15); ax.set_ylim(0,2.1); ax.axis('off')
xs=[.04,1.85,3.66,5.47]; w=1.64
for x,title in zip(xs,['1  DISCOVER','2  BUILD','3  EVALUATE','4  PUBLISH']):
 ax.text(x,2.02,title,fontsize=9,fontweight='bold',va='top',color='#173042')
model=['Search sources\nDefine a fixed task','Generate Python\nRepair saved code','Inspect meaning\nAccept / repair / reject',None]
code=['Validate proposal\nSave source and task','Run worker checks\nFit fixed baseline','Require checks\nRoute review decision','Transfer to both hosts\nVerify public files']
def box(x,y,text,color,edge):
 ax.add_patch(FancyBboxPatch((x,y),w,.51,boxstyle='round,pad=0.025,rounding_size=0.04',facecolor=color,edgecolor=edge,lw=.8))
 ax.text(x+w/2,y+.255,text,ha='center',va='center',fontsize=8.4,linespacing=1.45,color='#173042')
for x,m,c in zip(xs,model,code):
 if m:
  box(x,1.3,m,'#e7f0f7','#39759c')
  ax.add_patch(FancyArrowPatch((x+w/2,1.28),(x+w/2,1.11),arrowstyle='-|>',mutation_scale=9,color='#536570',lw=.9))
 box(x,.57,c,'#e5f2ed','#377b67')
for i in range(3):
 ax.add_patch(FancyArrowPatch((xs[i]+w+.04,.82),(xs[i+1]-.04,.82),arrowstyle='-|>',mutation_scale=10,color='#536570',lw=1))
ax.plot([xs[2]+w/2,xs[2]+w/2,xs[1]+w/2],[.54,.30,.30],color='#a36524',lw=1)
ax.add_patch(FancyArrowPatch((xs[1]+w/2,.30),(xs[1]+w/2,.54),arrowstyle='-|>',mutation_scale=9,color='#a36524',lw=1))
ax.text(3.57,.14,'Repair: saved proposal + specific findings',ha='center',va='center',fontsize=7.8,color='#805021')
ax.text(6.29,1.57,'Standing policy\nNo per-release approval',ha='center',va='center',fontsize=8.2,color='#52636b',linespacing=1.45)
ax.text(.04,.16,'Blue: bounded model task\nGreen: deterministic operation',fontsize=7.1,color='#52636b',va='center')
fig.savefig(out,metadata={'CreationDate':None,'ModDate':None})
print(out)
