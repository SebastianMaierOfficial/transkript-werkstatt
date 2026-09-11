import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

class LauncherTests(unittest.TestCase):
 def test_fresh_start_reuse_and_shutdown_in_path_with_spaces(self):
  with tempfile.TemporaryDirectory(prefix='transkript test ') as directory:
   root=Path(directory)
   shutil.copyfile(ROOT/'start.py',root/'start.py')
   shutil.copytree(ROOT/'app',root/'app',ignore=shutil.ignore_patterns('__pycache__'))
   http=urllib.request.build_opener(urllib.request.ProxyHandler({}))
   state=None
   try:
    for _ in range(2):
     subprocess.run([sys.executable,str(root/'start.py'),'--no-open'],check=True,timeout=30)
     current=json.loads((root/'.runtime/state.json').read_text())
     if state:self.assertEqual(current,state)
     state=current
    request=urllib.request.Request(f"http://127.0.0.1:{state['port']}/health",headers={'X-Session':state['token']})
    with http.open(request,timeout=5) as response:self.assertEqual(json.load(response)['version'],'1.0.0')
   finally:
    if state:
     request=urllib.request.Request(f"http://127.0.0.1:{state['port']}/shutdown",data=b'{}',headers={'X-Session':state['token'],'Content-Type':'application/json'})
     with http.open(request,timeout=5) as response:self.assertTrue(json.load(response)['ok'])
     import time
     for _ in range(100):
      if not (root/'.runtime/state.json').exists():break
      time.sleep(.05)

if __name__=='__main__':unittest.main(verbosity=2)
