"""Activity sequence: separate model generation from deterministic execution."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

root = Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
fig, ax = plt.subplots(figsize=(7.15, 1.92))
fig.subplots_adjust(0, 0, 1, 1)
ax.set(xlim=(0, 7.15), ylim=(0, 1.92)); ax.axis('off')
ink = '#173042'
xs = [.04, 1.50, 2.96, 4.42, 5.88]
w = 1.23

def arrow(a, b):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=9,
        lw=1, color=ink, shrinkA=0, shrinkB=0))

activities = [
    ('MODEL', 'Find a source;\npropose a task'),
    ('MODEL', 'Generate the\nPython builder'),
    ('CODE', 'Run the builder,\nchecks, and\nfixed baseline'),
    ('MODEL', 'Review\ntask meaning'),
    ('CODE', 'Publish files;\nverify access on\nboth platforms'),
]
for i, (x, (actor, label)) in enumerate(zip(xs, activities)):
    model = actor == 'MODEL'
    ax.add_patch(FancyBboxPatch((x, .82), w, .70,
        boxstyle='round,pad=0.01,rounding_size=0.035', lw=1,
        linestyle=(0, (3, 2)) if model else '-',
        facecolor='#e8f0f8' if model else '#e5f1e9',
        edgecolor='#31688a' if model else '#286349'))
    ax.text(x+w/2, 1.40, actor, ha='center', va='center',
        fontsize=8.7, fontweight='bold', color=ink)
    ax.text(x+w/2, 1.11, label, ha='center', va='center',
        fontsize=9.1, linespacing=1.12, color=ink)
    if i < 4:
        arrow((x+w+.025, 1.17), (xs[i+1]-.025, 1.17))

# Semantic and execution repairs return to builder generation.
a, b = xs[3]+w/2, xs[1]+w/2
ax.plot([a, a, b], [1.535, 1.73, 1.73], lw=1, color=ink)
arrow((b, 1.73), (b, 1.535))
ax.text((a+b)/2, 1.77, 'Semantic repair (up to four returns)',
        ha='center', va='bottom', fontsize=9.1, color=ink)
worker = xs[2]+w/2
ax.plot([worker, worker, b], [.805, .65, .65], lw=1, color=ink)
arrow((b, .65), (b, .805))
ax.text((worker+b)/2, .47, 'Execution repair (diagnostics)',
        ha='center', va='center', fontsize=9.1, color=ink)
ax.add_patch(FancyBboxPatch((.04, .04), 7.07, .28,
    boxstyle='round,pad=0.008,rounding_size=0.025',
    facecolor='#f2f4f5', edgecolor='#7c878e', lw=.7))
ax.text(3.575, .18,
    'Controller (code): stage transitions, saved state, retries, and worker management',
    ha='center', va='center', fontsize=9.1, color=ink)
fig.savefig(root/'draft/figures/workflow.pdf',
            metadata={'CreationDate': None, 'ModDate': None})
plt.close(fig)
print(root/'draft/figures/workflow.pdf')
