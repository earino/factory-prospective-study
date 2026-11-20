"""Run unmodified Hermes with HTTP body capture for Ollama inference only.

Headers (including authentication) are never stored. Stream bytes are forwarded
unchanged, while retaining request/response bodies for research inspection.
"""
import itertools,json,os,runpy,sys,threading,time
from pathlib import Path
from urllib.parse import urlsplit
import httpx
OUT=Path(os.environ.pop('SBIR_CAPTURE_DIR'));OUT.mkdir(parents=True,exist_ok=True)
_counter=itertools.count(1);_lock=threading.Lock()
def begin(request):
 url=urlsplit(str(request.url))
 if url.hostname!='ollama.com' or request.method!='POST':return None
 with _lock:n=next(_counter)
 stem=OUT/f'call-{n:03d}'
 body=request.content
 try:json.loads(body)
 except Exception:return None
 stem.with_suffix('.request.json').write_bytes(body)
 stem.with_suffix('.meta.json').write_text(json.dumps({'method':request.method,'url':str(request.url),'started_epoch':time.time()}))
 return stem
class SyncCapture(httpx.SyncByteStream):
 def __init__(self,stream,path):self.stream,self.path=stream,path
 def __iter__(self):
  with self.path.open('wb') as f:
   for chunk in self.stream:f.write(chunk);f.flush();yield chunk
 def close(self):self.stream.close()
class AsyncCapture(httpx.AsyncByteStream):
 def __init__(self,stream,path):self.stream,self.path=stream,path
 async def __aiter__(self):
  with self.path.open('wb') as f:
   async for chunk in self.stream:f.write(chunk);f.flush();yield chunk
 async def aclose(self):await self.stream.aclose()
_original=httpx.Client.send
_original_async=httpx.AsyncClient.send
def send(self,request,*a,**kw):
 stem=begin(request)
 try:response=_original(self,request,*a,**kw)
 except Exception as e:
  if stem:stem.with_suffix('.error.json').write_text(json.dumps({'type':type(e).__name__}))
  raise
 if stem:
  stem.with_suffix('.status.json').write_text(json.dumps({'status_code':response.status_code}))
  path=stem.with_suffix('.response.body')
  if response.is_stream_consumed:path.write_bytes(response.content)
  else:response.stream=SyncCapture(response.stream,path)
 return response
async def asend(self,request,*a,**kw):
 stem=begin(request)
 try:response=await _original_async(self,request,*a,**kw)
 except Exception as e:
  if stem:stem.with_suffix('.error.json').write_text(json.dumps({'type':type(e).__name__}))
  raise
 if stem:
  stem.with_suffix('.status.json').write_text(json.dumps({'status_code':response.status_code}))
  path=stem.with_suffix('.response.body')
  if response.is_stream_consumed:path.write_bytes(response.content)
  else:response.stream=AsyncCapture(response.stream,path)
 return response
httpx.Client.send=send;httpx.AsyncClient.send=asend
script=sys.argv[1];sys.argv=sys.argv[1:];sys.path.insert(0,str(Path(script).parent))
runpy.run_path(script,run_name='__main__')
