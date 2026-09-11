import sys, unittest, io, zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'app'))
import server as m
from overrides import validate_rules
from local_model import block_outgoing_network

def rule(source,target=None):return {'source':source,'action':'keep' if target is None else 'replace','target':target or ''}
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):pass
 def run_text(self,text,rules,**kw):return m.analyze(text,{},overrides=rules,**kw)['text']
 def test_roles_and_other_entities_model(self):
  text='Sebastian: Wie geht es Petra?\nPetra: Ich habe Thomas Müller in München getroffen.\nSebastian: Petra, was brauchst du?'
  self.assertEqual(self.run_text(text,[rule('Sebastian','Coach'),rule('Petra','Kundin')],mode='model'),'Coach: Wie geht es Kundin?\nKundin: Ich habe [Person] in [Ort] getroffen.\nCoach: Kundin, was brauchst du?')
 def test_keep_name(self):
  self.assertEqual(self.run_text('Sebastian: Petra kennt Sebastian.',[rule('Sebastian')],mode='model'),'Sebastian: [Person] kennt Sebastian.')
 def test_no_rules_unchanged(self):
  self.assertEqual(self.run_text('Sebastian: Petra kennt Thomas.',[]),'[Sprecher]: [Person] kennt [Person].')
 def test_word_boundaries_case_genitive(self):
  self.assertEqual(self.run_text('Sebastian und SEBASTIAN kennen Petras Idee und Sebastianismus.',[rule('Sebastian','Coach'),rule('Petra','Kundin')],auto_names=False,speakers=False),'Coach und Coach kennen Kundins Idee und Sebastianismus.')
 def test_keep_exact_spelling(self):
  self.assertEqual(self.run_text('Petras Idee und PETRA.',[rule('Petra')],speakers=False),'Petras Idee und PETRA.')
 def test_no_reprocessing_or_chaining(self):
  self.assertEqual(self.run_text('Sebastian kennt Petra.',[rule('Sebastian','Petra'),rule('Petra','Kundin')]),'Petra kennt Kundin.')
 def test_longest_wins(self):
  for rules in ([rule('Sebastian','Coach'),rule('Sebastian Maier','Trainer')],[rule('Sebastian Maier','Trainer'),rule('Sebastian','Coach')]):
   self.assertEqual(self.run_text('Sebastian Maier: Sebastian spricht.',rules),'Trainer: Coach spricht.')
 def test_residual_surname_not_exposed(self):
  text=self.run_text('Sebastian Maier spricht mit Petra Müller.',[rule('Sebastian','Coach'),rule('Petra','Kundin')],mode='model')
  self.assertEqual(text,'Coach [Person] spricht mit Kundin [Person].')
 def test_speaker_full_label(self):
  self.assertEqual(self.run_text('Sebastian Maier: Petra Müller hilft.',[rule('Sebastian','Coach'),rule('Petra','Kundin')],mode='model'),'Coach: Kundin [Person] hilft.')
 def test_rules_override_terms_and_exclusions(self):
  self.assertEqual(m.analyze('Petra: Petra kennt Thomas.',{'person':['Petra']},overrides=[rule('Petra','Kundin')],excluded=['Petra'])['text'],'Kundin: Kundin kennt [Person].')
 def test_speakers_off(self):
  self.assertEqual(self.run_text('Sebastian: Petra hilft.',[rule('Sebastian','Coach'),rule('Petra','Kundin')],speakers=False),'Coach: Kundin hilft.')
 def test_conflicting_and_invalid_rules(self):
  for rules in ([rule('Petra','Kundin'),rule('PETRA')],[rule('','Coach')],[rule('Petra','')],[rule('Petra','a\nb')],{}):
   with self.assertRaises(ValueError):validate_rules(rules)
  self.assertEqual(len(validate_rules([rule('Petra','Kundin'),rule('PETRA','Kundin')])),1)
 def test_export_contains_no_mapping(self):
  result=self.run_text('Sebastian: Petra hilft.',[rule('Sebastian','Coach'),rule('Petra','Kundin')])
  with zipfile.ZipFile(io.BytesIO(m.make_export([{'text':result,'reviewed':True}]))) as z:
   self.assertEqual(z.namelist(),['transkript-001.txt']);self.assertEqual(z.read(z.namelist()[0]).decode(),'Coach: Kundin hilft.')
 def test_adjacent_rules(self):
  self.assertEqual(self.run_text('Sebastian Petra Müller',[rule('Sebastian','Coach'),rule('Petra','Kundin')],mode='model',speakers=False),'Coach Kundin [Person]')
if __name__=='__main__':unittest.main(verbosity=2)
