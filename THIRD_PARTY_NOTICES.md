# Third-party notices and redistribution review

Reviewed for the initial source release on 2026-09-11. The repository contains original application code and a derived static dictionary, not vendored Python, third-party library binaries or model weights. Dependencies/model are installed separately from their original distribution channels. Their own licenses continue to apply; this project's MIT license does not replace them. This is a source/license inventory, not a legal guarantee about every possible use.

## Presidio

- Presidio Analyzer and Anonymizer: 2.2.360, MIT.
- https://github.com/data-privacy-stack/presidio
- https://presidio.dataprivacystack.org/
- License copy: [licenses/Presidio-MIT.txt](licenses/Presidio-MIT.txt).
- Used for local NLP integration and replacement operators. No remote recognizers configured. Not an official Presidio project.

## spaCy and German model

- spaCy 3.8.16: MIT. https://github.com/explosion/spaCy
- `de_core_news_lg` 3.8.0: MIT, Copyright 2021 ExplosionAI GmbH.
- Model source: https://github.com/explosion/spacy-models/releases/tag/de_core_news_lg-3.8.0
- Documentation: https://spacy.io/models/de
- License copies: [spaCy](licenses/spaCy-MIT.txt), [model](licenses/spaCy-model-MIT.txt), [model source notices](licenses/spaCy-model-SOURCES.txt).
- The model package describes TIGER Corpus (commercially licensed by Explosion), Tiger2Dep (citation, no code bundled), WikiNER (CC BY 4.0) and Explosion fastText Vectors trained on OSCAR Common Crawl + Wikipedia (CC0) in its source notices. Those notices are retained verbatim here. We do not redistribute the training corpora or claim rights to them.
- Model weights are unmodified and downloaded from the official release at installation. `requirements-model.txt` pins URL and SHA-256. The model is trained on written German news, not evaluated here for coaching-transcript anonymity.

## Faker-derived names.json

- Faker 37.12.0, MIT. https://github.com/joke2k/faker/tree/v37.12.0/faker/providers/person
- Copyright notice and permission: [licenses/Faker-MIT.txt](licenses/Faker-MIT.txt).
- `app/names.json` is a derived, deduplicated union of first/family name entries from locales `de_DE`, `de_AT`, `de_CH`, `en_US`, `fr_FR`, `it_IT`, `tr_TR`, `es_ES`, `pl_PL`, `nl_NL`.
- Modification: list extraction/combination into JSON for deterministic recognition. This is not a database of the application's users. Faker itself is not called at runtime and no fake replacement identities are generated.

## Runtime, installer and transitive dependencies

- Python: PSF license, separately installed. https://docs.python.org/3/license.html
- uv (optional): MIT OR Apache-2.0, separately installed. https://github.com/astral-sh/uv
- Exact Python-package versions are in `requirements.txt`. Their distributions retain their upstream metadata and license files in `.venv`. This source release does not repackage them. Any future binary/standalone installer must re-audit all bundled transitive dependencies and include their notices; the present source-only review does not cover such a bundle.
- GitHub Actions and Node's built-in test runner are development infrastructure, not required for offline processing. No user transcripts are used in CI.

Names/logos of upstream projects identify dependencies only, with no implied endorsement. Preserve these notices when sharing this project or its dictionary. The MIT notices allow redistribution, subject to retaining their copyright/permission notices. Nothing here establishes legal anonymization or excludes mandatory statutory liability.
