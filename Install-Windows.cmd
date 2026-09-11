@echo off
setlocal
cd /d "%~dp0"
where uv >nul 2>nul
if not errorlevel 1 (
  uv run --python 3.12 --no-project install.py
) else (
  py -3.12 install.py
)
if errorlevel 1 echo Installation fehlgeschlagen. Bitte docs\INSTALLATION.md lesen.
pause
