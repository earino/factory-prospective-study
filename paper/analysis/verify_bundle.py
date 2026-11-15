"""Build the portable source in a clean directory and verify the delivered PDF."""
from pathlib import Path
import hashlib,json,re,subprocess,tempfile,zipfile
P=Path(__file__).resolve().parents[1]; out=P/'output'; clean=Path(tempfile.mkdtemp(prefix='factory-paper-source-check-'))
with zipfile.ZipFile(out/'paper-source.zip') as z:z.extractall(clean)
with (out/'clean-build.txt').open('w') as f:subprocess.run(['sh','build.sh'],cwd=clean,stdout=f,stderr=subprocess.STDOUT,check=True)
info=subprocess.check_output(['pdfinfo',str(clean/'main.pdf')],text=True)
pages=int(re.search(r'Pages:\s+(\d+)',info).group(1));assert 1 <= pages <= 7,pages
log=(clean/'main.log').read_text();assert 'Overfull' not in log and 'undefined' not in log
fonts=subprocess.check_output(['pdffonts',str(clean/'main.pdf')],text=True);assert 'Type 3' not in fonts
for line in fonts.splitlines()[2:]:assert line.split()[-5]=='yes',line
subprocess.run(['pdftotext',str(clean/'main.pdf'),str(clean/'clean.txt')],check=True)
subprocess.run(['pdftotext',str(out/'paper.pdf'),str(out/'check.txt')],check=True)
assert (clean/'clean.txt').read_text()==(out/'check.txt').read_text()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
checks={'pages':pages,'template':'IEEEtran conference, 10pt, letter','clean_source_bundle_build':True,'clean_and_workspace_text_identical':True,'unresolved_references':False,'overfull_boxes':False,'all_fonts_embedded':True,'type3_fonts':False,'source_bundle_sha256':sha(out/'paper-source.zip'),'pdf_sha256':sha(out/'paper.pdf'),'evidence_snapshot_sha256':sha(P/'analysis/draft-inputs.json'),'consumer_update_sha256':sha(P/'analysis/update-inputs-2026-11-15.json'),'evening_update_sha256':sha(P/'analysis/evening-inputs-2026-11-15.json')}
if (P/'analysis/final-inputs-2026-11-16.json').exists():
 checks['final_snapshot_sha256']=sha(P/'analysis/final-inputs-2026-11-16.json')
(out/'QA.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
