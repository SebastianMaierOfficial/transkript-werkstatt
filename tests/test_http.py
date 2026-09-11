import base64
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]

class HttpTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.state=Path(cls.temp.name)/'state.json'
  cls.process=subprocess.Popen([sys.executable,str(ROOT/'app/server.py'),'--state',str(cls.state)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for _ in range(200):
   if cls.state.exists():break
   if cls.process.poll() is not None:raise RuntimeError('Test server exited')
   time.sleep(.05)
  data=json.loads(cls.state.read_text());cls.url=f"http://127.0.0.1:{data['port']}";cls.token=data['token']
  cls.http=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 @classmethod
 def tearDownClass(cls):
  cls.process.terminate();cls.process.wait(timeout=10);cls.temp.cleanup()
 def call(self,path,data=None,**headers):
  request=urllib.request.Request(self.url+path,data=None if data is None else json.dumps(data).encode(),headers={'X-Session':self.token,'Content-Type':'application/json',**headers})
  return self.http.open(request,timeout=60)
 def test_single_txt(self):
  with self.call('/export',{'documents':[{'text':'Coach: Kundin spricht.','reviewed':True}]}) as response:
   self.assertEqual(response.headers.get_content_type(),'text/plain')
   self.assertIn('transkript-001.txt',response.headers['Content-Disposition'])
   self.assertEqual(response.read().decode(),'Coach: Kundin spricht.')
 def test_multiple_zip(self):
  with self.call('/export',{'documents':[{'text':text,'reviewed':True} for text in ['eins','zwei']]}) as response:
   self.assertEqual(response.headers.get_content_type(),'application/zip')
   with zipfile.ZipFile(io.BytesIO(response.read())) as z:
    self.assertEqual(z.namelist(),['transkript-001.txt','transkript-002.txt']);self.assertEqual(z.read('transkript-002.txt'),b'zwei')
 def test_review_and_auth_required(self):
  for headers,body,expected in [({}, {'documents':[{'text':'x','reviewed':False}]},400),({'X-Session':'wrong'},{},403),({'Origin':'https://example.invalid'},{},403)]:
   with self.assertRaises(urllib.error.HTTPError) as error:self.call('/export',body,**headers)
   self.assertEqual(error.exception.code,expected)
 def test_batch_docx_txt_and_refine(self):
  doc=io.BytesIO()
  with zipfile.ZipFile(doc,'w') as z:z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Petra: Ich wohne in München.</w:t></w:r></w:p></w:body></w:document>')
  config={'mode':'model','auto_names':True,'speakers':True,'overrides':[{'source':'Petra','action':'replace','target':'Kundin'}]}
  files=[{'name':name,'data':base64.b64encode(data).decode()} for name,data in [('example.docx',doc.getvalue()),('example.txt',b'Sebastian: Petra kennt Thomas Zappelwitz.')]]
  with self.call('/process',dict(config,files=files)) as response:results=json.load(response)['results']
  self.assertEqual(results[0]['text'],'Kundin: Ich wohne in [Ort].');self.assertEqual(results[1]['text'],'[Sprecher]: Kundin kennt [Person].')
  with self.call('/refine',dict(config,text=results[0]['original'],excluded=['München'])) as response:self.assertEqual(json.load(response)['text'],'Kundin: Ich wohne in München.')
 def test_offline_child(self):
  subprocess.run([sys.executable,str(ROOT/'offline_check.py')],cwd=ROOT,check=True,timeout=90)
 def test_start_reuses_server(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('portable_start',ROOT/'start.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  module.STATE=self.state
  self.assertEqual(module.alive()['port'],int(self.url.rsplit(':',1)[1]))

if __name__=='__main__':unittest.main(verbosity=2)
