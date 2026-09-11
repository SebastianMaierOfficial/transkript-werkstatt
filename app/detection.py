"""Deterministic dictionary and context heuristics. No trained models."""
import json
from pathlib import Path
import re
import unicodedata

DATA = json.loads((Path(__file__).parent / 'names.json').read_text())
FIRST = {unicodedata.normalize('NFC', n).casefold() for n in DATA['first']}
LAST = {unicodedata.normalize('NFC', n).casefold() for n in DATA['last']}
# Words/names with frequent non-person uses. Context may still identify them.
AMBIGUOUS = set('am an als also art april august bei bin chance das dem den der des die doch du ein eine einer eines ernst es etwas frank frei für gegen gerade gut hallo heute hier ich ihr ihre im in ist ja jede jetzt kann kein keine klar komm liebe mai man mark mehr mich mit morgen muss nach nein nicht nichts nun oder ohne rose sage schon schön sein seine selbst sie so soll sonntag tag und uns von vor wann war was weg weil wenn wer wie will wir wohl zu zum zur herr frau dr professor coach klient klientin sprecher speaker person teilnehmer teilnehmerin therapeut therapeutin'.split())
WORD = re.compile(r"[^\W\d_]+(?:[-’'][^\W\d_]+)*", re.UNICODE)
NAME = r"[A-ZÀ-ÖØ-Þ][^\W\d_]*(?:[-’'][^\W\d_]+)*"
ROLE = re.compile(r'^(?:coach|klient(?:in)?|sprecher(?:in)?|speaker|person|teilnehmer(?:in)?|therapeut(?:in)?|interviewer|interviewee|moderator(?:in)?)(?:[ _-]*\d+)?$', re.I)

def literal(term):
    pattern = r'\s+'.join(re.escape(x) for x in term.split())
    return (r'(?<!\w)' if term[0].isalnum() else '') + pattern + (r'(?!\w)' if term[-1].isalnum() else '')

def speaker_spans(text):
    return list(re.finditer(r'(?m)^[ \t]*(?:\[[^\]\n]{1,40}\][ \t]*)?([^\n:]{1,80}):[ \t]*', text))

def candidates(text):
    found = {}
    def add(name, source):
        name = name.strip()
        if len(name) < 2 or len(name) > 150 or ROLE.fullmatch(name): return
        key = name.casefold()
        found.setdefault(key, {'name':name, 'source':source})
    tokens = list(WORD.finditer(text))
    for i, match in enumerate(tokens):
        word = match.group(); key = word.casefold()
        base = key[:-1] if key.endswith('s') and key[:-1] in FIRST else key
        if not word[0].isupper() or key in AMBIGUOUS or base in AMBIGUOUS: continue
        if key in FIRST or base in FIRST:
            add(word[:-1] if key not in FIRST and base != key else word, 'Vornamenliste')
            # Adjacent family names from the dictionary; never span sentence punctuation.
            if i+1 < len(tokens):
                nxt=tokens[i+1]; tail=nxt.group()
                if text[match.end():nxt.start()].strip()=='' and '\n' not in text[match.end():nxt.start()] and tail[0].isupper() and tail.casefold() in LAST and tail.casefold() not in AMBIGUOUS:
                    add(text[match.start():nxt.end()], 'Vor- und Nachname')
                    add(tail, 'Nachname aus vollständigem Namen')
    contexts = [
        (r'(?i:\b(?:Herrn?|Frau|Dr\.|Doktor|Professor(?:in)?)\s+)('+NAME+r'(?:[ \t]+'+NAME+r')?)', 'Anrede'),
        (r'(?i:\b(?:mein(?:e|en|em|er)?|unser(?:e|en|em|er)?)\s+(?:Bruder|Schwester|Mutter|Vater|Sohn|Tochter|Partner(?:in)?|Freund(?:in)?|Kolleg(?:e|in)|Chef(?:in)?|Mann|Frau)\s+)('+NAME+r')', 'Beziehungsangabe'),
        (r'(?i:\b(?:heiße|heißt|heissen|heißen|namens)\s+)('+NAME+r')', 'Namensnennung'),
    ]
    for pattern, source in contexts:
        for match in re.finditer(pattern,text):
            name=match.group(1)
            words=name.split()
            # Avoid swallowing a capitalized common noun after a title.
            if len(words)>1 and words[-1].casefold() in AMBIGUOUS: name=words[0]
            if name.casefold() not in AMBIGUOUS or name.casefold() in FIRST:
                add(name,source)
                for word in name.split(): add(word,source)
    for match in speaker_spans(text):
        label=match.group(1).strip()
        words=WORD.findall(label)
        if ROLE.fullmatch(label) or not 1<=len(words)<=4: continue
        if any(w.casefold() in FIRST and w.casefold() not in AMBIGUOUS for w in words):
            add(label,'Sprechername')
            for word in words:
                if word.casefold() not in AMBIGUOUS: add(word,'Sprechername')
    # Expose base and genitive together so both can be reviewed/excluded.
    for value in found.values():
        name=value['name']; suffix = r'(?:s|[’\x27]s?)?' if name[-1].isalpha() else ''
        pattern=literal(name)
        if suffix and pattern.endswith(r'(?!\w)'): pattern=pattern[:-6]+suffix+r'(?!\w)'
        value['count']=sum(1 for _ in re.finditer(pattern,text,re.I))
    return sorted(found.values(),key=lambda v:v['name'].casefold())

def person_pattern(name):
    p=literal(name)
    if name[-1].isalpha() and p.endswith(r'(?!\w)'):
        p=p[:-6]+r'(?:s|[’\x27]s?)?(?!\w)'
    return p


def person_label(matched, name):
    actual = ' '.join(matched.casefold().split())
    base = ' '.join(name.casefold().split())
    return '[Person]s' if actual != base and actual.startswith(base) else '[Person]'
