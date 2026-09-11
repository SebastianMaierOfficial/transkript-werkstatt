# Instructions for installation and development agents

This is a local German transcript-redaction assistant. Read README.md, docs/INSTALLATION.md and docs/BEDIENUNG.md before installing or explaining it. Never claim guaranteed anonymization or regulatory compliance.

## Install and hand over

1. Determine OS, architecture, a writable local destination and available Python/uv. Support target: Python 3.12, macOS and Windows x64; Linux is also covered by CI. Do not claim untested devices are verified.
2. Use the official repository or release source; extract the entire folder. Do not copy another computer's `.venv`, runtime files or private data.
3. Install an up-to-date Python 3.12 using existing uv if needed. If uv is missing, use its official installation documentation or an available trusted package manager. Explain that initial setup downloads Python, packages and a ~568 MB German model. No transcript is needed for setup. Do not disable certificate checks, antivirus, Gatekeeper or global PowerShell policy.
4. Run `uv run --python 3.12 --no-project install.py`, or `python3.12 install.py` / `py -3.12 install.py`. The installer creates a project-local `.venv` and runs `offline_check.py`. Never install project dependencies into system Python. Read failures and fix them; don't silently fall back to rules-only.
5. Confirm the offline check passes with the installed environment: `.venv/bin/python offline_check.py` (Mac/Linux) or `.venv\Scripts\python.exe offline_check.py` (Windows). It uses only synthetic data and blocks outgoing Python socket/DNS calls.
6. Start via `Start-Mac.command` / `Start-Windows.cmd`, or the environment's Python plus `start.py`. `--no-open` is available for test runners. Verify `/health` using the local `.runtime/state.json` token; never publish that token or file. Verify the browser opens the app and process its built-in fictional example. Do not read existing user transcript sessions without explicit need and authorization.
7. Explain to the user: subsequent start/processing needs no internet; one reviewed text downloads as TXT and multiple as ZIP; the browser controls the destination folder. Its Downloads setting can ask for a location each time. No original filename or rule mapping is exported. Original files are untouched.
8. Explain roles (`Sebastian → Coach`, `Petra → Kundin`) and optional keep rules, manual review of names AND identifying context, and the difference between clearing the UI and quitting the server. No claim that role replacements alone make data anonymous. Show the limitations and MIT warranty notice.

## Privacy boundaries

- Never upload user transcripts, filenames, extracted names, screenshots of private sessions, exception lists, state tokens or real data to GitHub, cloud AI, issues, logs or test fixtures.
- Use invented fixtures. Keep all application inference local; no telemetry, CDN assets, remote recognizers or model auto-download during startup/processing.
- Bind only 127.0.0.1; retain Host, Origin, session-token and CSP protections. Python network audit hooks are defense in depth, not an OS sandbox.
- Do not persist transcript content or reusable identity mappings. Exclude `.venv`, `.runtime`, logs, exports and local caches from commits and releases. Users' OS backups, swap, browser extensions and synchronized folders remain outside the app's control.
- Do not restart an active user service or overwrite unexported results while testing. Test separate server instances with temporary state.

## Development and releases

Run `.venv/bin/python -m unittest discover -s tests -v` (Windows: `.venv\Scripts\python.exe`), `node --check app/app.js`, and `node --test tests/replacement.test.cjs`. Node is test-only. Run a fresh install and the GitHub Actions OS matrix for changes to requirements/install/start. Browser-test changed UI using synthetic content. Distinguish automated Windows checks from manual Windows-browser testing.

Keep requirements versioned and the model URL/hash pinned. Retain `LICENSE`, `THIRD_PARTY_NOTICES.md` and upstream notices for the Faker-derived dictionary and model sources. Do not package virtual environments, model weights or third-party binaries in source releases. Audit the staged file list and diff for private paths/secrets/data before publishing. Release only when the documented gates pass; record any actual limitations honestly. Do not create draft pull requests; any PR must be review-ready.
