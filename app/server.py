#!/usr/bin/env python3
"""Local-only Presidio desktop companion. Transcript contents never written to disk."""
import argparse
import base64
import io
import json
import os
from pathlib import Path
import re
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from socketserver import TCPServer
import threading
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

from overrides import validate_rules, rule_spans, prioritize
from local_model import model_candidates, block_outgoing_network
from detection import candidates, literal, person_pattern, person_label, speaker_spans
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, RecognizerResult

ROOT = Path(__file__).resolve().parent
MAX_FILE = 10 * 1024 * 1024
MAX_BODY = 65 * 1024 * 1024
MAX_TEXT = 2_000_000
PATTERNS = [
    r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
    r"(?:https?://|www\.)[^\s<>]+",
    r"(?<!\w)[A-Z]{2}\d{2}(?:[ \t]?[A-Z0-9]){11,30}(?!\w)",
    r"(?<!\w)(?:\+\d{1,3}[ \t-]?|00\d{1,3}[ \t-]?|0)(?:\(?\d\)?[ \t/.-]?){6,14}\d(?!\d)",
    r"(?<!\d)(?:0?[1-9]|[12]\d|3[01])\.(?:0?[1-9]|1[0-2])\.(?:19|20)\d{2}(?!\d)",
]


def extract(data, filename):
    if len(data) > MAX_FILE:
        raise ValueError("Datei zu groß: maximal 10 MB pro Datei.")
    suffix = Path(filename).suffix.lower()
    if suffix == '.txt':
        try:
            text = data.decode('utf-8-sig')
        except UnicodeDecodeError:
            raise ValueError("TXT bitte als UTF-8 speichern.")
    elif suffix == '.docx':
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                info = archive.getinfo('word/document.xml')
                if info.file_size > 20 * 1024 * 1024:
                    raise ValueError("Entpackter Dokumenttext zu groß.")
                xml = archive.read(info)
            if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():
                raise ValueError("Nicht unterstützte XML-Struktur.")
            root = ET.fromstring(xml)
            ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            for tag in ('ins', 'del', 'moveFrom', 'moveTo', 'txbxContent', 'altChunk'):
                if next(root.iter(ns + tag), None) is not None:
                    raise ValueError("DOCX enthält Änderungen oder komplexe Inhalte. Bitte in Word als TXT exportieren.")
            body = root.find(ns + 'body')
            if body is None:
                raise ValueError("Kein Dokumenthaupttext gefunden.")
            paragraphs = []
            for paragraph in body.iter(ns + 'p'):
                chunks = []
                for node in paragraph.iter():
                    if node.tag == ns + 't':
                        chunks.append(node.text or '')
                    elif node.tag == ns + 'tab':
                        chunks.append('\t')
                    elif node.tag in (ns + 'br', ns + 'cr'):
                        chunks.append('\n')
                paragraphs.append(''.join(chunks))
            text = '\n'.join(paragraphs)
        except (zipfile.BadZipFile, KeyError, ET.ParseError, RuntimeError):
            raise ValueError("DOCX nicht lesbar. Bitte in Word als TXT exportieren.")
    else:
        raise ValueError("Nur TXT und DOCX werden unterstützt.")
    if len(text) > MAX_TEXT:
        raise ValueError("Maximal 2 Millionen Zeichen pro Dokument.")
    if not text.strip():
        raise ValueError("Die Datei enthält keinen lesbaren Haupttext.")
    return unicodedata.normalize('NFC', text.replace('\r\n', '\n').replace('\r', '\n'))


LABELS = {'person': '[Person]', 'place': '[Ort]', 'company': '[Unternehmen]', 'other': '[Angabe]'}

def settings(body):
    terms = body.get('terms', {})
    if not isinstance(terms, dict) or set(terms) - set(LABELS):
        raise ValueError('Ungültige Begriffsliste.')
    for values in terms.values():
        if not isinstance(values, list) or len(values) > 2000 or any(not isinstance(t,str) or len(t)>2000 for t in values):
            raise ValueError('Ungültige Begriffsliste.')
    excluded = body.get('excluded', [])
    if not isinstance(excluded, list) or len(excluded)>15000 or any(not isinstance(t,str) or len(t)>200 for t in excluded):
        raise ValueError('Ungültige Ausnahmen.')
    if body.get('mode', 'model') not in ('model', 'rules'):
        raise ValueError('Ungültiger Erkennungsmodus.')
    return terms, body.get('numbers') is True, body.get('speakers') is True, body.get('auto_names') is True, excluded, body.get('mode', 'model'), validate_rules(body.get('overrides', []))


def analyze(text, terms, numbers=False, speakers=True, auto_names=True, excluded=(), mode="rules", overrides=()):
    custom = rule_spans(text, validate_rules(list(overrides)))
    hits = []
    def add(pattern, label):
        hits.extend((m.start(),m.end(),label) for m in re.finditer(pattern,text,re.I))
    for pattern, label in zip(PATTERNS, ('[E-Mail]', '[Link]', '[Kontonummer]', '[Telefonnummer]', '[Datum]')):
        add(pattern,label)
    for kind, values in terms.items():
        for value in values:
            term=unicodedata.normalize('NFC',value.strip())
            if term:
                if kind=='person':
                    hits.extend((m.start(),m.end(),person_label(m.group(),term)) for m in re.finditer(person_pattern(term),text,re.I))
                else: add(literal(term),LABELS[kind])
    names=[dict(item,kind='person') for item in candidates(text)] if auto_names else []
    if mode == 'model':
        model_names=model_candidates(text)
        names=list({item['name'].casefold():item for item in names+model_names}.values())
    names.sort(key=lambda item:item['name'].casefold())
    exclusions=[m.span() for name in excluded if name.strip() for m in re.finditer(person_pattern(name.strip()),text,re.I)]
    for name in names:
        pattern=person_pattern(name['name']) if name['kind']=='person' else literal(name['name'])
        for match in re.finditer(pattern,text,re.I):
            if not any(match.start()<end and match.end()>start for start,end in exclusions):
                label=person_label(match.group(),name['name']) if name['kind']=='person' else LABELS[name['kind']]
                hits.append((match.start(),match.end(),label))
    if numbers: add(r'\d+(?:[.,:/-]\d+)*','[Zahl]')
    if speakers:
        for match in speaker_spans(text):
            explicit = [h for h in custom if h[0] >= match.start(1) and h[1] <= match.end(1)]
            if explicit:
                role = ' / '.join(dict.fromkeys(h[2] for h in explicit))
                custom = [h for h in custom if h not in explicit]
                custom.append((match.start(), match.end(), role + ': '))
            else:
                hits.append((match.start(), match.end(), '[Sprecher]: '))
    hits = prioritize(text, hits, custom)
    merged=[]
    for start,end,label in sorted(hits,key=lambda h:(h[0],-h[1],h[2])):
        if merged and start<merged[-1][1]:
            prev=merged[-1]
            if end>prev[1]:
                prev[1]=end
                if prev[2]!=label: prev[2]='[Angabe]'
            # Contained hits keep the category of the outer text (e.g. an email).
        else: merged.append([start,end,label])
    spans=[];operators={}
    for i,(start,end,label) in enumerate(merged):
        entity='MATCH_'+str(i)
        spans.append(RecognizerResult(entity_type=entity,start=start,end=end,score=1.0))
        operators[entity]=OperatorConfig('replace',{'new_value':label})
    result=AnonymizerEngine().anonymize(text,spans,operators).text if spans else text
    return {'text':result,'count':sum(text[start:end] != label for start,end,label in merged),'candidates':names}


def make_export(documents):
    if not isinstance(documents, list) or not 1 <= len(documents) <= 50:
        raise ValueError("Bitte 1 bis 50 geprüfte Texte auswählen.")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as archive:
        for index, doc in enumerate(documents, 1):
            if not isinstance(doc, dict) or doc.get('reviewed') is not True:
                raise ValueError("Jeden Text vor dem Speichern prüfen und bestätigen.")
            text = doc.get('text')
            if not isinstance(text, str) or len(text) > MAX_TEXT:
                raise ValueError("Ungültiger Ausgabetext.")
            info = zipfile.ZipInfo(f'transkript-{index:03}.txt', date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, text.encode('utf-8'))
    return buf.getvalue()


def make_download(documents):
    # Same validation and neutral filenames for both export paths.
    archive = make_export(documents)
    if len(documents) == 1:
        return documents[0]['text'].encode('utf-8'), 'text/plain; charset=utf-8', 'transkript-001.txt'
    return archive, 'application/zip', 'gepruefte-transkripte.zip'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, code, content, kind='application/json; charset=utf-8', download_name=None):
        if not isinstance(content, bytes):
            content = json.dumps(content, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        if download_name:
            self.send_header('Content-Disposition', f'attachment; filename="{download_name}"')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        try:
            self.wfile.write(content)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def valid_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

    def authorized(self):
        token = self.headers.get('X-Session', '')
        origin = self.headers.get('Origin')
        return (self.valid_host() and secrets.compare_digest(token, self.server.token)
                and origin in (None, f'http://127.0.0.1:{self.server.server_port}'))

    def do_GET(self):
        if not self.valid_host():
            return self.reply(403, {'error': 'Zugriff abgelehnt.'})
        if self.path == '/health' and self.authorized():
            return self.reply(200, {'app': 'transkript-werkstatt', 'version': '1.0.2', 'model': 'de_core_news_lg 3.8.0', 'outgoing_network': 'blocked'})
        files = {'/': ('index.html', 'text/html; charset=utf-8'), '/replacement.js': ('replacement.js','text/javascript; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if self.path not in files:
            return self.reply(404, {'error': 'Nicht gefunden.'})
        name, kind = files[self.path]
        self.reply(200, (ROOT / name).read_bytes(), kind)

    def do_POST(self):
        if not self.authorized():
            return self.reply(403, {'error': 'Sitzung ungültig. Programm erneut öffnen.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BODY:
                return self.reply(413, {'error': 'Auswahl zu groß. Bitte einen kleineren Stapel verarbeiten.'})
            self.connection.settimeout(60)
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError('Ungültige Anfrage.')
            if self.path == '/process':
                files = body.get('files')
                config = settings(body)
                if not isinstance(files, list) or not 1 <= len(files) <= 50:
                    raise ValueError('Bitte 1 bis 50 Dateien auswählen.')
                results = []
                for entry in files:
                    try:
                        if not isinstance(entry, dict) or not isinstance(entry.get('name'), str):
                            raise ValueError('Ungültige Datei.')
                        data = base64.b64decode(entry.get('data', ''), validate=True)
                        original = extract(data, entry['name'])
                        results.append(dict(analyze(original,*config),original=original))
                    except (ValueError, TypeError) as error:
                        # Messages here are fixed validation messages, never raw XML/input.
                        message = str(error) if type(error) is ValueError else 'Datei nicht lesbar.'
                        results.append({'error': message})
                self.reply(200, {'results': results})
            elif self.path == '/refine':
                text = body.get('text')
                if not isinstance(text,str) or len(text)>MAX_TEXT:
                    raise ValueError('Ungültiger Text.')
                self.reply(200, analyze(text,*settings(body)))
            elif self.path == '/export':
                content, kind, filename = make_download(body.get('documents'))
                self.reply(200, content, kind, filename)
            elif self.path == '/shutdown':
                self.reply(200, {'ok': True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                self.reply(404, {'error': 'Nicht gefunden.'})
        except (ValueError, TypeError, OSError):
            self.reply(400, {'error': 'Anfrage nicht lesbar oder unvollständig. Bitte Auswahl und Prüfstatus kontrollieren.'})
        except Exception:
            self.reply(500, {'error': 'Verarbeitung fehlgeschlagen. Keine Ergebnisse gespeichert.'})


class LoopbackServer(ThreadingHTTPServer):
    def server_bind(self):
        # HTTPServer's default calls getfqdn(), which can block on offline DNS.
        TCPServer.server_bind(self)
        self.server_name = 'localhost'
        self.server_port = self.server_address[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', required=True, type=Path)
    args = parser.parse_args()
    block_outgoing_network()
    server = LoopbackServer(('127.0.0.1', 0), Handler)
    server.token = secrets.token_urlsafe(32)
    server.daemon_threads = True
    args.state.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    state = {'port': server.server_port, 'token': server.token, 'pid': os.getpid()}
    fd = os.open(args.state, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as handle:
        json.dump(state, handle)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        args.state.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
