"""Portable launcher. Only loopback health checks; never installs/downloads at startup."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent
STATE = ROOT / '.runtime' / 'state.json'
# Ignore HTTP_PROXY/HTTPS_PROXY even for the local health check.
LOCAL_HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def alive():
    try:
        state = json.loads(STATE.read_text(encoding='utf-8'))
        if not isinstance(state['port'], int) or not 1 <= state['port'] <= 65535:
            return None
        request = urllib.request.Request(f"http://127.0.0.1:{state['port']}/health", headers={'X-Session': state['token']})
        with LOCAL_HTTP.open(request, timeout=1) as response:
            result = json.load(response)
            if result.get('app') == 'transkript-werkstatt' and result.get('version') == '1.0.0':
                return state
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-open', action='store_true', help='Start without opening a browser')
    args = parser.parse_args()
    state = alive()
    if not state:
        STATE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        process_options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
        child = subprocess.Popen([sys.executable, str(ROOT / 'app' / 'server.py'), '--state', str(STATE)],
                                 cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, **process_options)
        for _ in range(150):
            state = alive()
            if state or child.poll() is not None:
                break
            time.sleep(.1)
    if not state:
        print('Start fehlgeschlagen. Installation erneut ausführen oder mit der .venv-Python-Version offline_check.py starten.')
        return 1
    url = f"http://127.0.0.1:{state['port']}/#{state['token']}"
    if not args.no_open and not webbrowser.open(url):
        print('Browser nicht automatisch geöffnet. Diese lokale Adresse im Browser öffnen:')
        print(url)
    else:
        print('Transkript-Werkstatt läuft lokal. Beenden über den Button im Browser.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
