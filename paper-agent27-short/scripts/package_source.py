"""Create a portable LaTeX source archive without research data or credentials."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[1]
paths=[root/'build.sh',*sorted((root/'draft').rglob('*'))]
with ZipFile(root/'output/paper-source.zip','w',ZIP_DEFLATED) as archive:
 for path in paths:
  if path.is_file(): archive.write(path,Path('paper-agent27-short')/path.relative_to(root))
 archive.writestr('paper-agent27-short/README.md', '''# Portable AGENT 2027 paper source

Run `sh build.sh` with a LaTeX installation providing pdflatex and bibtex.
The included IEEEtran class/style, figures and generated table require no study
checkout, Python environment, or external data for the PDF build.
The result is `output/paper.pdf`.

Figure-generation scripts and the evidence supporting the paper remain in the
study repository's `paper-agent27-short/` directory. This archive reproduces the
manuscript, not new factory production or new consumer-model trajectories.
''')
print(root/'output/paper-source.zip')
