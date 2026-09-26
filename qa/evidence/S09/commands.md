# S09 command evidence

Exact argument vectors, exit codes, environment and outputs are in each record.

| Evidence | Command | Exit |
|---|---|---:|
| [s09a-commands](s09a-commands.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_cli_commands.py tests/test_bootstrap.py` | 0 |
| [s09b-policy](s09b-policy.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_cli_policy.py tests/test_cli_commands.py` | 0 |
| [s09c-journey-tests](s09c-journey-tests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_cli_journey.py` | 1 |
| [formatting](formatting.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/cli.py src/neurocvguard/__main__.py src/neurocvguard/__init__.py src/neurocvguard/workflows.py src/neurocvguard/reporting.py tests/test_bootstrap.py tests/test_cli_commands.py tests/test_cli_policy.py tests/test_cli_journey.py qa/evidence/S09` | 0 |
| [lint-initial](lint-initial.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [mypy-initial](mypy-initial.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 |
| [s09c-corrected](s09c-corrected.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_cli_journey.py` | 0 |
| [journey-editable](journey-editable.json) | `.venv/Scripts/python.exe -I qa/evidence/S09/run_journey.py` | 0 |
| [format-ready](format-ready.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/cli.py tests/test_cli_journey.py qa/evidence/S09` | 0 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S09/pytest-final.xml` | 0 |
| [lint-final](lint-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [environment](environment.json) | `.venv/Scripts/python.exe -m pip list --format=json` | 0 |
| [install-ordinary](install-ordinary.json) | `.venv-install/Scripts/python.exe -m pip install .` | 1 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [install-ordinary-retry](install-ordinary-retry.json) | `.venv-install/Scripts/python.exe -m pip install .` | 0 |
| [journey-ordinary](journey-ordinary.json) | `.venv-install/Scripts/python.exe -I qa/evidence/S09/run_journey.py --ordinary` | 0 |
| [journey-editable-utf8](journey-editable-utf8.json) | `.venv/Scripts/python.exe -I qa/evidence/S09/run_journey.py` | 0 |
| [closeout-map](closeout-map.json) | `python qa/evidence/S09/close_stage.py finish` | 0 |
| [preservation](preservation.json) | `python qa/evidence/S09/close_stage.py verify` | 0 |
| [environment-ordinary](environment-ordinary.json) | `.venv-install/Scripts/python.exe -m pip list --format=json` | 0 |
| [evidence-format](evidence-format.json) | `.venv/Scripts/python.exe -m ruff format --check qa/evidence/S09/run_journey.py` | 0 |
| [diff-check](diff-check.json) | `git diff --check` | 0 |
