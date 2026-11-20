"""Index model-visible tool results for inspection; no network or inference."""
import hashlib,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent
TERMS=['factory-prospective-study',r'dataset.factory','earino',r'selection.declaration',
       'no outcome field',r'semantic.review','sbir-acceptance','v-0d2e623e604ecf78']

def audit():
 rows=[];hits=[]
 for d in sorted((BASE/'runs').glob('*')):
  records=json.loads((d/'session-records.json').read_text())
  for index,m in enumerate(records['messages']):
   if m['role']!='tool':continue
   text=m['content']
   urls=sorted(set(re.findall(r'https?://[^\s\"<>\\]+',text)))
   row={'run_id':d.name,'message_index':index,'tool':m['tool_name'],
        'content_sha256':hashlib.sha256(text.encode()).hexdigest(),'urls':urls}
   rows.append(row)
   for term in TERMS:
    for match in re.finditer(term,text,re.I):
     hits.append({'run_id':d.name,'message_index':index,'term':term,
                  'excerpt':text[max(0,match.start()-200):match.end()+300]})
 return {'tool_results':len(rows),'screen_terms':TERMS,'screen_hits':hits,'records':rows,
         'scope':'Literal/regex screening plus retained URL inventory. No proof of absence of prior model exposure or indirect semantic exposure.'}

if __name__=='__main__':
 result=audit();(BASE/'results/tool-exposure.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Indexed',result['tool_results'],'tool results;',len(result['screen_hits']),'screen hits')
