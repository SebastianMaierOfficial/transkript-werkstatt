import sys, unittest, io, zipfile, socket
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'app'))
import server as m
from local_model import block_outgoing_network, chunks

class ModelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  pass
 def process(self,text,**kwargs):
  return m.analyze(text,{},speakers=False,mode='model',**kwargs)
 def test_full_names_surnames_locations_organizations(self):
  text='Ich habe mit Thomas Zappelwitz gesprochen. Zappelwitz kennt Anna von Winterfels. Winterfels arbeitet in München. Morgen fahren wir nach Hamburg. Meine Kollegin Claudia arbeitet bei Siemens.'
  r=self.process(text)
  self.assertEqual(r['text'],'Ich habe mit [Person] gesprochen. [Person] kennt [Person]. [Person] arbeitet in [Ort]. Morgen fahren wir nach [Ort]. Meine Kollegin [Person] arbeitet bei [Unternehmen].')
  self.assertEqual({i['kind'] for i in r['candidates']},{'person','place','company'})
 def test_multiword_places(self):
  r=self.process('Thomas Müller hat angerufen. Müller kommt aus Bad Tölz. Wir treffen uns in Berlin bei der Deutschen Bahn.')
  for word in ('Thomas','Müller','Bad Tölz','Berlin','Deutschen Bahn'):self.assertNotIn(word,r['text'])
  self.assertIn('[Unternehmen]',r['text'])
 def test_no_common_word_regression(self):
  text='Das ist mein Ernst. Ich will morgen arbeiten. Meine Arbeit ist gut. Wir reden über Hilfe und Liebe.'
  self.assertEqual(self.process(text)['text'],text)
 def test_genitive(self):
  self.assertEqual(self.process("Annas Idee und Thomas' Vorschlag.")['text'],'[Person]s Idee und [Person]s Vorschlag.')
 def test_excluded_place_and_manual_priority(self):
  text='Ich wohne in München.'
  self.assertEqual(self.process(text,excluded=['München'])['text'],text)
  self.assertEqual(m.analyze(text,{'place':['München']},mode='model',excluded=['München'])['text'],'Ich wohne in [Ort].')
 def test_chunk_boundary(self):
  text=('Wir sprechen über die Arbeit. '*1050)+'Thomas Zappelwitz wohnt in München. Zappelwitz hilft.'
  r=self.process(text)
  self.assertNotIn('Zappelwitz',r['text']);self.assertNotIn('München',r['text'])
  self.assertEqual(r['text'].count('Wir sprechen über die Arbeit.'),1050)
 def test_docx_and_export(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Thomas Müller lebt in München.</w:t></w:r></w:p></w:body></w:document>')
  original=m.extract(b.getvalue(),'privater-name.docx');r=self.process(original)
  with zipfile.ZipFile(io.BytesIO(m.make_export([{'text':r['text'],'reviewed':True}]))) as z:
   self.assertEqual(z.namelist(),['transkript-001.txt']);self.assertEqual(z.read(z.namelist()[0]).decode(),'[Person] lebt in [Ort].')
  with self.assertRaises(ValueError):m.make_export([{'text':r['text'],'reviewed':False}])
 def test_model_failure_no_silent_fallback(self):
  import local_model
  engine=local_model._engine
  from unittest.mock import patch
  with patch.object(engine,'analyze',side_effect=RuntimeError('private input must not surface')):
   with self.assertRaisesRegex(ValueError,'nicht auf reine Regeln'):self.process('Thomas Müller')
 def test_mode_validation(self):
  self.assertEqual(m.settings({'mode':'rules'})[-2],'rules')
  with self.assertRaises(ValueError):m.settings({'mode':'remote'})

if __name__=='__main__':unittest.main(verbosity=2)
