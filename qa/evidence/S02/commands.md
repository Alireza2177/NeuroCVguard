# S02 command evidence

Exact argument vectors, exit codes, environment and outputs are in each record.

| Evidence | Command | Exit |
|---|---|---:|
| [s02a-tables](s02a-tables.json) | `.venv/Scripts/python.exe -m pytest -q tests/test_input_tables.py --strict-markers --strict-config` | 0 |
| [s02b-features](s02b-features.json) | `.venv/Scripts/python.exe -m pytest -q tests/test_feature_inputs.py --strict-markers --strict-config` | 1 |
| [s02b-corrected](s02b-corrected.json) | `.venv/Scripts/python.exe -m pytest -q tests/test_feature_inputs.py --strict-markers --strict-config` | 0 |
| [s02c-guards](s02c-guards.json) | `.venv/Scripts/python.exe -m pytest -q tests/test_input_guards.py --strict-markers --strict-config` | 0 |
| [format](format.json) | `.venv/Scripts/python.exe -m ruff format src tests qa/evidence/S02` | 0 |
| [mypy-initial](mypy-initial.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [lint-initial](lint-initial.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [imports-fix](imports-fix.json) | `.venv/Scripts/python.exe -m ruff check src tests qa/evidence/S02 --select I --fix` | 0 |
| [format-ready](format-ready.json) | `.venv/Scripts/python.exe -m ruff format src tests docs/input_tables.md qa/evidence/S02` | 0 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S02/pytest-final.xml` | 0 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [lint-check](lint-check.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [environment](environment.json) | `.venv/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 |
| [lint-final](lint-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 |
| [closeout-map](closeout-map.json) | `.venv/Scripts/python.exe qa/evidence/S02/close_stage.py finish` | 0 |
| [preservation](preservation.json) | `.venv/Scripts/python.exe qa/evidence/S02/close_stage.py verify` | 0 |
| [diff-check](diff-check.json) | `git diff --check` | 0 |
