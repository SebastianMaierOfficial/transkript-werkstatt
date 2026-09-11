#!/bin/bash
cd "$(dirname "$0")" || exit 1
if [ ! -x .venv/bin/python ]; then
  echo 'Bitte zuerst Install-Mac.command ausführen.'
  read -r -p 'Enter zum Schliessen …' _answer
  exit 1
fi
.venv/bin/python start.py
