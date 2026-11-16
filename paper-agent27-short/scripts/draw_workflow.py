"""Production contracts and observed milestones; original 7.15 x 2.1 in footprint."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

root=Path(__file__).resolve().parents[1]
checks=json.loads((root/'analysis/record-checks.json').read_text())
assert checks['milestones']=={'discover':54,'build':18,'evaluate':14,'publish':14}
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(7.15,2.1))
fig.subplots_adjust(0,0,1,1)
ax.set_xlim(0,7.15);ax.set_ylim(0,2.1);ax.axis('off')
xs=[.04,1.85,3.66,5.47];w=1.64
ink='#173042';line='#48535a';fs=8.6

def text(x,y,s,**kw):
    return ax.text(x,y,s,fontsize=fs,color=ink,**kw)
def arrow(a,b,**kw):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=8,
                               lw=.85,color=line,shrinkA=0,shrinkB=0,**kw))
def box(x,y,h,label,model=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,
        boxstyle='round,pad=0.012,rounding_size=0.025',
        facecolor='#e8f0f8' if model else '#e5f1e9',
        edgecolor='#31688a' if model else '#286349',
        linestyle=(0,(3,2)) if model else '-',lw=1))
    text(x+w/2,y+h/2,label,ha='center',va='center',linespacing=1.05)

for x,stage,count in zip(xs,['DISCOVER','BUILD','EVALUATE','PUBLISH'],
                        ['54 completed','18 completed',None,'14 published']):
    text(x+w/2,2.055,stage,ha='center',va='top',fontweight='bold')
    if count:text(x+w/2,1.88,count,ha='center',va='top')

models=['Propose source and task','Generate / repair Python','Review task meaning']
returns=['structured proposal\nor deferral','Python builder\n+ task metadata','accept / repair / reject\n+ findings']
for x,label,result in zip(xs[:3],models,returns):
    box(x,1.12,.28,label,model=True)
    arrow((x+.07,1.095),(x+.07,.815))
    text(x+.87,.955,result,ha='center',va='center',linespacing=1.02)

# Input annotation is neutral and feeds the review model. No causal assertion.
text(xs[2]+w/2,1.88,'Review packet: builder,\nchecks, selected\ndescriptor fields',
     ha='center',va='top',linespacing=1.02)
arrow((xs[2]+w/2,1.51),(xs[2]+w/2,1.425))

ops=['Validate proposal\nSave source and task',
     'Run worker checks\nFit fixed baseline',
     'Require checks\nRoute review decision',
     'Standing policy:\nno per-release approval\nTransfer to both hosts\nVerify public files']
for x,label in zip(xs,ops):box(x,.25,.54,label)
# Execution order: accepted discovery feeds code generation, then the worker
# output feeds the review model. There is no green-to-green bypass of a model.
build_input=1.745
ax.plot([xs[0]+w+.012,build_input,build_input],[.52,.52,1.26],lw=.85,color=line)
arrow((build_input,1.26),(xs[1]-.025,1.26))
arrow((xs[2]+w+.025,.52),(xs[3]-.025,.52))

# A single outgoing path carries the worker result to semantic review.
spine=3.555
ax.plot([xs[1]+w+.012,spine,spine,xs[2]+w/2],
        [.67,.67,1.51,1.51],lw=.75,color=line)

# Four returns to construction; a further repair is deferred (Section II-B).
x0=xs[2]+w/2
ax.plot([x0,x0,build_input,build_input],[.225,.16,.16,.52],lw=.85,color=line)
arrow((build_input,.32),(build_input,.48))
text((x0+build_input)/2,.015,'≤4 semantic returns',ha='center',va='bottom')
fig.savefig(root/'draft/figures/workflow.pdf',metadata={'CreationDate':None,'ModDate':None})
plt.close(fig)
print(root/'draft/figures/workflow.pdf')
