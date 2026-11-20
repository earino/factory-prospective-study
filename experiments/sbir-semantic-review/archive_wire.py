"""Losslessly compress completed HTTP bodies; leave local originals intact."""
import gzip,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
rows=[]
for group in ['runs','smoke']:
 for d in sorted((BASE/group).glob('*')):
  if not (d/'finished.json').exists():continue
  for p in sorted((d/'wire').glob('*.response.body')):
   raw=p.read_bytes();encoded=gzip.compress(raw,mtime=0)
   dest=Path(str(p)+'.gz')
   if dest.exists():assert gzip.decompress(dest.read_bytes())==raw,p
   else:dest.write_bytes(encoded)
   assert gzip.decompress(dest.read_bytes())==raw,p
   rows.append({'path':str(dest.relative_to(BASE)),'uncompressed_sha256':hashlib.sha256(raw).hexdigest(),'uncompressed_bytes':len(raw),'compressed_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(BASE/'wire-archive.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Verified lossless archives:',len(rows))
