"""Prepare and verify the arXiv source without changing the submitted manuscript."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryDirectory
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'arxiv'
NOTICE = ('This work has been submitted to the IEEE for possible publication. '
          'Copyright may be transferred without notice, after which this version may no longer be accessible.')
sha = lambda data: hashlib.sha256(data).hexdigest()
DEST.mkdir(exist_ok=True)
source = ROOT / 'draft'
submitted_pdf = ROOT / 'output/paper.pdf'
original_pdf_hash = sha(submitted_pdf.read_bytes())
files = {str(p.relative_to(source)): p.read_bytes() for p in source.rglob('*') if p.is_file()}
assert all(Path(p).suffix in {'.tex', '.bib', '.bst', '.cls', '.pdf'} for p in files)
original_tex = files['main.tex']
tex = original_tex.decode()
# First-page footer in the existing margin: preserve the submitted text layout.
tex = tex.replace(r'\usepackage[hidelinks]{hyperref}', r'\usepackage[hidelinks]{hyperref}' + '\n' + r'\usepackage{eso-pic}')
footer = (r'\AddToShipoutPictureFG*{\AtPageLowerLeft{'
          r'\put(\LenToUnit{0.5in},\LenToUnit{0.22in}){'
          r'\parbox{\dimexpr\paperwidth-1in\relax}{\footnotesize\centering ' + NOTICE + r'}}}}')
tex = tex.replace(r'\begin{document}', r'\begin{document}' + '\n' + footer)
files['main.tex'] = tex.encode()
files['main.bbl'] = (ROOT / 'output/main.bbl').read_bytes()
assert len(re.findall(rb'\\bibitem', files['main.bbl'])) == 17
archive = DEST / 'dataset-factory-arxiv.zip'
with ZipFile(archive, 'w', ZIP_DEFLATED) as z:
    for name, data in sorted(files.items()):
        z.writestr(name, data)
with TemporaryDirectory(prefix='factory-arxiv-check-') as folder:
    folder = Path(folder)
    with ZipFile(archive) as z:
        z.extractall(folder)
    for _ in range(3):
        subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-no-shell-escape', 'main.tex'],
                       cwd=folder, check=True, capture_output=True)
    log = (folder / 'main.log').read_text()
    for bad in ['Overfull', 'undefined references', 'Rerun to get']:
        assert bad not in log, bad
    pdf = folder / 'main.pdf'
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    assert re.search(r'Pages:\s+5\b', info)
    def text(p):
        return ' '.join(subprocess.check_output(['pdftotext', '-layout', str(p), '-'], text=True).split())
    preview_text = text(pdf)
    assert preview_text.count(NOTICE) == 1
    assert ' '.join(preview_text.replace(NOTICE, '').split()) == text(submitted_pdf)
    (DEST / 'preview.pdf').write_bytes(pdf.read_bytes())
assert sha(submitted_pdf.read_bytes()) == original_pdf_hash
report = {
    'entrypoint': 'main.tex', 'compiler': 'pdflatex', 'pages': 5,
    'source_archive_sha256': sha(archive.read_bytes()),
    'preview_sha256': sha((DEST / 'preview.pdf').read_bytes()),
    'submitted_pdf_sha256': original_pdf_hash,
    'submitted_tex_sha256': sha(original_tex),
    'source_files': {p: {'bytes': len(data), 'sha256': sha(data)} for p, data in sorted(files.items())},
    'change_from_submitted_paper': 'IEEE submission notice in first-page footer only; body text, figures and layout preserved.',
    'notice': NOTICE, 'compiled_bibliography_entries': 17,
    'clean_build': 'Three pdflatex passes from extracted archive, no BibTeX run or shell escape.',
    'body_text_matches_submission': True, 'submitted_pdf_unchanged': True,
    'no_overfull_or_unresolved_references': True,
    'policy_sources': ['https://info.arxiv.org/help/submit_tex.html',
                       'https://info.arxiv.org/help/prep.html',
                       'https://conferences.ieeeauthorcenter.ieee.org/get-published/post-your-paper/']
}
(DEST / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'zip': str(archive), 'preview': str(DEST / 'preview.pdf'), 'pages': 5,
                  'files': len(files), 'body_text_matches_submission': True}))
