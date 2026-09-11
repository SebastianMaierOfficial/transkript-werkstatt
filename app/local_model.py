"""Installed German NER only. No downloads, remote recognizers or transcript cache."""
import re
import sys
import threading

from detection import AMBIGUOUS, FIRST, WORD, literal, person_pattern

MODEL = 'de_core_news_lg'
KINDS = {'PERSON': 'person', 'LOCATION': 'place', 'ORGANIZATION': 'company'}
_engine = None
_lock = threading.Lock()


def block_outgoing_network():
    # Process-wide CPython guard; accepted localhost HTTP connections still work.
    # This is defense in depth, not an OS firewall against arbitrary native code.
    def guard(event, args):
        if event in {'socket.connect', 'socket.getaddrinfo', 'socket.gethostbyname',
                     'socket.gethostbyaddr', 'socket.sendto', 'socket.sendmsg'}:
            raise OSError('Ausgehende Netzwerkverbindungen sind gesperrt.')
    sys.addaudithook(guard)


def _load():
    import spacy
    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
    from presidio_analyzer.nlp_engine import SpacyNlpEngine, NerModelConfiguration
    from presidio_analyzer.predefined_recognizers import SpacyRecognizer

    class InstalledEngine(SpacyNlpEngine):
        def load(self):
            # Intentionally bypass Presidio's automatic download-if-missing behavior.
            self.nlp = {'de': spacy.load(MODEL)}

    nlp = InstalledEngine(models=[{'lang_code': 'de', 'model_name': MODEL}],
        ner_model_configuration=NerModelConfiguration(
            model_to_presidio_entity_mapping={'PER': 'PERSON', 'LOC': 'LOCATION', 'ORG': 'ORGANIZATION'},
            labels_to_ignore=['MISC'], low_score_entity_names=[]))
    registry = RecognizerRegistry(supported_languages=['de'])
    registry.add_recognizer(SpacyRecognizer(supported_language='de', supported_entities=list(KINDS)))
    return AnalyzerEngine(nlp_engine=nlp, registry=registry, supported_languages=['de'], log_decision_process=False)


def chunks(text, size=30000, overlap=500):
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            while end < len(text) and not text[end].isspace():
                end += 1
        yield start, text[start:end]
        if end == len(text):
            break
        start = end - overlap
        while start > 0 and not text[start-1].isspace():
            start -= 1


def model_candidates(text):
    global _engine
    found = {}
    def add(name, kind, source):
        name = ' '.join(name.split())
        if kind == 'person' and name.casefold() not in FIRST and name.endswith('s') and name[:-1].casefold() in FIRST:
            name = name[:-1]
        if 1 < len(name) <= 200 and name.casefold() not in AMBIGUOUS:
            found.setdefault(name.casefold(), {'name': name, 'kind': kind, 'source': source})
    with _lock:
        try:
            if _engine is None:
                _engine = _load()
            for offset, part in chunks(text):
                for hit in _engine.analyze(text=part, language='de', entities=list(KINDS)):
                    name = part[hit.start:hit.end]
                    kind = KINDS[hit.entity_type]
                    add(name, kind, 'Lokales Sprachmodell')
                    if kind == 'person':
                        words = WORD.findall(name)
                        # Carry first/last components to later mentions in this document.
                        # Lowercase name particles are never replaced on their own.
                        if len(words) > 1:
                            for word in words:
                                if word[0].isupper():
                                    add(word, kind, 'Bestandteil eines erkannten Namens')
        except Exception:
            raise ValueError('Lokales Modell konnte nicht ausgeführt werden. Es wurde nicht auf reine Regeln zurückgeschaltet. Bitte App-Installation prüfen.') from None
    for item in found.values():
        pattern = person_pattern(item['name']) if item['kind'] == 'person' else literal(item['name'])
        item['count'] = sum(1 for _ in re.finditer(pattern, text, re.I))
    return list(found.values())
