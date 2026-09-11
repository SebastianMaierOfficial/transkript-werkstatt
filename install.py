"""One-time online setup. Does not read any transcripts or change system Python."""
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def main():
    if sys.version_info[:2] != (3, 12):
        print('Bitte Python 3.12 verwenden. Siehe docs/INSTALLATION.md.')
        return 1
    environment = ROOT / '.venv'
    if not environment.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    try:
        subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
                        '-r', str(ROOT / 'requirements.txt'), '-r', str(ROOT / 'requirements-model.txt')],
                       cwd=ROOT, check=True)
        subprocess.run([str(python), str(ROOT / 'offline_check.py')], cwd=ROOT, check=True)
    except (OSError, subprocess.CalledProcessError):
        print('Installation nicht abgeschlossen. Meldung oben prüfen; danach Installation erneut starten.')
        return 1
    print('Installation und Offline-Selbsttest erfolgreich. Jetzt Start-Mac.command bzw. Start-Windows.cmd öffnen.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
