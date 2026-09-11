import base64, importlib.util, io, json, sys, unittest, urllib.request, urllib.error, zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'app'))
import server as m
class Tests(unittest.TestCase):
 def test_embedded_names_no_manual_list(self):
  r=m.analyze('Coach: Ich habe mit Thomas Müller gesprochen. Thomas kennt Claudia.',{})
  self.assertEqual(r['text'],'[Sprecher]: Ich habe mit [Person] gesprochen. [Person] kennt [Person].')
  self.assertTrue(r['candidates'])
 def test_unknown_context_and_propagation(self):
  r=m.analyze('Meine Kollegin Xelunia hat angerufen. Xelunia hilft mir. Herr Zappelwitz kennt Zappelwitz.',{})
  self.assertEqual(r['text'],'Meine Kollegin [Person] hat angerufen. [Person] hilft mir. Herr [Person] kennt [Person].')
 def test_genitive(self):
  self.assertEqual(m.analyze('Annas Idee und Thomas\' Vorschlag.',{})['text'],'[Person]s Idee und [Person]s Vorschlag.')
 def test_typed_values(self):
  r=m.analyze('Ich spreche mit Max über München und Beispiel GmbH.',{'place':['München'],'company':['Beispiel GmbH']})
  self.assertEqual(r['text'],'Ich spreche mit [Person] über [Ort] und [Unternehmen].')
 def test_numbers_optional_and_contact(self):
  r=m.analyze('Ich habe 2 Kinder. E-Mail anna@example.org. Termin 12.08.2026.',{})
  self.assertIn('2 Kinder',r['text']);self.assertIn('[E-Mail]',r['text']);self.assertIn('[Datum]',r['text']);self.assertNotIn('anna@example.org',r['text'])
  self.assertIn('[Zahl] Kinder',m.analyze('Ich habe 2 Kinder.',{},numbers=True)['text'])
 def test_common_words(self):
  text='Das ist mein Ernst. Ich will morgen arbeiten. Meine Arbeit ist gut. Wir reden über Hilfe und Liebe.'
  self.assertEqual(m.analyze(text,{})['text'],text)
 def test_excluded_and_manual_priority(self):
  self.assertEqual(m.analyze('Anna hilft Anna.',{},excluded=['Anna'])['text'],'Anna hilft Anna.')
  self.assertEqual(m.analyze('Anna hilft Anna.',{'person':['Anna']},excluded=['Anna'])['text'],'[Person] hilft [Person].')
 def test_overlap(self):
  self.assertEqual(m.analyze('Anna Beispiel GmbH',{'company':['Anna Beispiel GmbH']})['text'],'[Unternehmen]')
  self.assertEqual(m.analyze('Alpha Beta Gamma',{'other':['Alpha Beta','Beta Gamma']},auto_names=False)['text'],'[Angabe]')
 def test_switch_off(self):
  self.assertEqual(m.analyze('Anna: Thomas hilft.',{},auto_names=False,speakers=False)['text'],'Anna: Thomas hilft.')
 def test_unknown_limit(self):
  text='Xyquella unterstützt das Team.'
  self.assertEqual(m.analyze(text,{})['text'],text)
 def test_export(self):
  r=m.analyze('Thomas und Claudia sprechen.',{})
  archive=m.make_export([{'text':r['text'],'reviewed':True}])
  with zipfile.ZipFile(io.BytesIO(archive)) as z:
   self.assertEqual(z.namelist(),['transkript-001.txt']);self.assertEqual(z.read(z.namelist()[0]).decode(),'[Person] und [Person] sprechen.')
  with self.assertRaises(ValueError):m.make_export([{'text':'hi','reviewed':False}])
 def test_no_models(self):
  import subprocess
  subprocess.run([sys.executable,'-c',"import sys; sys.path.insert(0,'app'); import server; server.analyze('Anna hilft.',{}); assert 'spacy' not in sys.modules; assert 'presidio_analyzer' not in sys.modules"],cwd=Path(__file__).resolve().parents[1],check=True)
if __name__=='__main__': unittest.main(verbosity=2)
