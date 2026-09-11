#!/bin/bash
cd "$(dirname "$0")" || exit 1
if command -v uv >/dev/null 2>&1; then
  uv run --python 3.12 --no-project install.py
elif command -v python3.12 >/dev/null 2>&1; then
  python3.12 install.py
else
  echo 'Python 3.12 oder uv fehlt. Bitte docs/INSTALLATION.md lesen.'
fi
read -r -p 'Enter zum Schliessen …' _answer
