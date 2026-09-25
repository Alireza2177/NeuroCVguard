# S07 exact command register

Commands ran from the project root in PowerShell. The recorder executes the
displayed argument vector without a child shell and sets PYTHONIOENCODING=utf-8.
Linked records contain actual UTC start times, recorder Python/platform,
stdout, stderr and exit status. Initial failures are retained. Use a fresh
record name to reproduce a command because evidence writes are exclusive.

| Exact command | Exit | Evidence |
|---|---:|---|
| `python qa/evidence/S07/run_check.py s07a-ledger .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_ledger.py` | 0 | [s07a-ledger.json](s07a-ledger.json) |
| `python qa/evidence/S07/run_check.py s07b-checks .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_preprocessing.py` | 1 | [s07b-checks.json](s07b-checks.json) |
| `python qa/evidence/S07/run_check.py s07b-corrected .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_preprocessing.py` | 0 | [s07b-corrected.json](s07b-corrected.json) |
| `python qa/evidence/S07/run_check.py s07c-boundaries .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_fit_boundaries.py` | 0 | [s07c-boundaries.json](s07c-boundaries.json) |
| `python qa/evidence/S07/run_check.py imports-fix .venv/Scripts/python.exe -m ruff check --select I,F401 --fix src/neurocvguard/audit.py src/neurocvguard/provenance.py src/neurocvguard/fit_boundaries.py src/neurocvguard/checks/preprocessing.py src/neurocvguard/rules.py src/neurocvguard/_projection.py src/neurocvguard/__init__.py tests/test_ledger.py tests/test_preprocessing.py tests/test_fit_boundaries.py` | 0 | [imports-fix.json](imports-fix.json) |
| `python qa/evidence/S07/run_check.py format-apply .venv/Scripts/python.exe -m ruff format src/neurocvguard/audit.py src/neurocvguard/provenance.py src/neurocvguard/fit_boundaries.py src/neurocvguard/checks/preprocessing.py src/neurocvguard/rules.py src/neurocvguard/_projection.py src/neurocvguard/__init__.py tests/test_ledger.py tests/test_preprocessing.py tests/test_fit_boundaries.py` | 0 | [format-apply.json](format-apply.json) |
| `python qa/evidence/S07/run_check.py mypy-initial .venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 | [mypy-initial.json](mypy-initial.json) |
| `python qa/evidence/S07/run_check.py lint-initial .venv/Scripts/python.exe -m ruff check .` | 1 | [lint-initial.json](lint-initial.json) |
| `python qa/evidence/S07/run_check.py format-followup .venv/Scripts/python.exe -m ruff format src/neurocvguard/audit.py src/neurocvguard/checks/preprocessing.py src/neurocvguard/fit_boundaries.py src/neurocvguard/rules.py tests/test_preprocessing.py docs/preprocessing_provenance.md` | 0 | [format-followup.json](format-followup.json) |
| `python qa/evidence/S07/run_check.py pytest-final .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S07/pytest-final.xml` | 0 | [pytest-final.json](pytest-final.json) |
| `python qa/evidence/S07/run_check.py mypy-final .venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 | [mypy-final.json](mypy-final.json) |
| `python qa/evidence/S07/run_check.py lint-final .venv/Scripts/python.exe -m ruff check .` | 0 | [lint-final.json](lint-final.json) |
| `python qa/evidence/S07/run_check.py environment-dev .venv/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 | [environment-dev.json](environment-dev.json) |
| `python qa/evidence/S07/run_check.py install-ordinary .venv-install/Scripts/python.exe -m pip install .` | 1 | [install-ordinary.json](install-ordinary.json) |
| `python qa/evidence/S07/run_check.py install-ordinary-retry .venv-install/Scripts/python.exe -m pip install .` | 0 | [install-ordinary-retry.json](install-ordinary-retry.json) |
| `python qa/evidence/S07/run_check.py helpers-format .venv/Scripts/python.exe -m ruff format qa/evidence/S07/check_installed.py qa/evidence/S07/check_closeout.py` | 0 | [helpers-format.json](helpers-format.json) |
| `python qa/evidence/S07/run_check.py diff-check git diff --check` | 0 | [diff-check.json](diff-check.json) |
| `python qa/evidence/S07/run_check.py doctests .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 | [doctests.json](doctests.json) |
| `python qa/evidence/S07/run_check.py format-final .venv/Scripts/python.exe -m ruff format --check .` | 0 | [format-final.json](format-final.json) |
| `python qa/evidence/S07/run_check.py lint-helpers .venv/Scripts/python.exe -m ruff check .` | 0 | [lint-helpers.json](lint-helpers.json) |
| `python qa/evidence/S07/run_check.py environment-installed .venv-install/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 | [environment-installed.json](environment-installed.json) |
| `python qa/evidence/S07/run_check.py installed-smoke .venv-install/Scripts/python.exe qa/evidence/S07/check_installed.py` | 0 | [installed-smoke.json](installed-smoke.json) |
| `python qa/evidence/S07/run_check.py closeout .venv/Scripts/python.exe qa/evidence/S07/check_closeout.py` | 0 | [closeout.json](closeout.json) |
| `python qa/evidence/S07/run_check.py final-diff-check git diff --check` | 0 | [final-diff-check.json](final-diff-check.json) |

The first install could not obtain hatchling inside restricted execution.
install-ordinary-retry used approved escalation in the existing isolated
project environment; no runtime dependency version was changed.
Full environment inventories are environment-dev.json and environment-installed.json.

Full regression: 320 passed; doctests: 7 passed. No skips. Closeout verifies
398 baseline files retained, 388 unchanged, 10 authorized modifications,
all 7 S07 mappings and unchanged predecessor/later-stage status and evidence.
JUnit normalization replaces only hostname with <LOCAL_HOST>; outcomes remain intact.

Initial Git status was clean at HEAD 2224dfd. No commit, push, publication
or later-stage implementation was performed. Final file hashes exclude
virtual environments, caches, bytecode, build outputs and the inventory itself.
