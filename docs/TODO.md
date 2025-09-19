# Production Hardening TODO

Legend: Priority (P0 critical, P1 important, P2 later) • Impact (High/Med/Low)

## P0 — High impact
- CI correctness (Impact: High)
  - Fix paths in .github/workflows/ci-cd.yml to target src/ not config/ for lint/coverage and bandit
    - Lint: lines 83-93 → change flake8/black/isort targets from config/ tests/ to src/ tests/
    - Tests coverage: line 48 → change --cov=config to --cov=src and ensure coverage.xml generated
    - Security: lines 121-123 → scan src/ and scripts, not config/
    - Build validation: line 161 → call scripts/validate_env.py (CLAUDE.md shows scripts/validate_env.py)
- Remove build artifacts from version control (Impact: High)
  - Add output/html/ and output/images/ to .gitignore and git rm --cached them; keep generated assets untracked
- Secrets handling & env validation (Impact: High)
  - Ensure all credentials come only from environment and are never logged
  - Add a startup validator in src/ (pydantic or simple checks) for: GCP_CREDENTIALS, TOGETHER_API_KEY, INSTAGRAM_USERNAME/PASSWORD, INSTAGRAM_DRIVE_FILE_ID, CRYPTO_SPREADSHEET_KEY
  - Optional: add detect-secrets or gitleaks to CI
- Dependency hygiene (Impact: High)
  - requirements.txt: deduplicate and pin versions; choose one of psycopg2 vs psycopg2-binary (prefer psycopg2-binary)
    - Duplicates/mismatches: google-auth libs repeated (lines 11-13 and 22-25), sqlalchemy repeated (19 and 31), psycopg2 and psycopg2-binary (5 and 33)
  - Remove mysql-connector-python unless actually needed (PostgreSQL is primary per CLAUDE.md)
  - Add a constraints file or pin with ~= for stability
- Script consolidation (Impact: High)
  - Merge src/scripts/instapost.py, instapost_new.py, instapost_restructured.py into single CLI entrypoint with flags (dry-run, template, limit)
  - Keep instapost_push.py focused on publishing only, with idempotency and rate limiting
- Template/assets consistency (Impact: Med)
  - Ensure each core_templates/N.html links styleN.css; centralize shared variables in a base stylesheet
  - Keep output/html/* strictly generated; no stylesheet checked in there

## P1 — Medium impact
- Configuration module (Impact: High)
  - Introduce src/config.py using pydantic-settings or a small wrapper around os.getenv with types and defaults
  - Single source of truth for paths (absolute), timezones, quality settings
- Structured logging & metrics (Impact: Med)
  - Add JSON logs (std out) with run/correlation IDs; integrate basic metrics (counts of posts, retries)
- Retry/backoff & timeouts (Impact: Med)
  - Standardize retry policy for network calls (requests, instagrapi, Google APIs) with exponential backoff and circuit-breaker semantics
- Type checking & static analysis (Impact: Med)
  - Add mypy config and CI step; increase typing in src/scripts/*.py
- Test strategy expansion (Impact: Med)
  - Unit tests for data transforms and Jinja context building
  - Integration tests: Playwright HTML render smoke (headless), mock Together/Google/Instagram
  - Snapshot tests of rendered HTML to detect template regressions
- Fonts and offline rendering (Impact: Med)
  - Self-host fonts or embed to avoid network dependency during Playwright runs

## P2 — Longer term
- Packaging & structure (Impact: Med)
  - Convert to a package (pyproject.toml), move scripts into a module with console_scripts entrypoints
  - Consider a services/ domain structure (render/, publish/, data/)
- Pre-commit hooks (Impact: Med)
  - black, isort, flake8, detect-secrets; mirror CI settings
- Containerization (Impact: Med)
  - Dockerfile with Playwright browsers layer; CI build and scan
- Releases & versioning (Impact: Low)
  - SemVer, automated changelog, GitHub Releases

## Quick file references
- Workflows: .github/workflows/ci-cd.yml:41-49, 83-93, 121-123, 158, 161
- Dependencies: requirements.txt:5,11-13,19,22-25,31,33
- Templates: core_templates/6.html:6 (now uses style6.css)
- Scripts to consolidate: src/scripts/instapost.py, src/scripts/instapost_new.py, src/scripts/instapost_restructured.py, src/scripts/instapost_push.py

## Execution order (suggested)
1) CI fixes and artifact ignore (P0) 2) Dependency cleanup (P0) 3) Secrets/env validation (P0) 4) Script consolidation (P0) 5) Logging/retries/config (P1) 6) Tests expansion (P1) 7) Fonts/offline (P1) 8) Packaging/pre-commit/containerization (P2)
