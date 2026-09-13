# S03 recorded command history

Each JSON record preserves the exact argument vector, UTC timestamp, working
directory, interpreter/platform, environment overrides, exit code and captured
output. Local paths are privacy-normalized. The recorder uses no shell.
Failed intermediate attempts are retained; see review.md for corrections.

| Evidence | Exact command (PowerShell quoting) | Exit |
|---|---|---|
| [s03a-inventory](s03a-inventory.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_cohort_inventory.py` | 0 |
| [s03b-components](s03b-components.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_identity.py tests/test_cohort_inventory.py` | 0 |
| [s03c-equality](s03c-equality.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_cohort_checks.py` | 0 |
| [mypy-initial](mypy-initial.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 |
| [regression-initial](regression-initial.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config` | 0 |
| [format-source](format-source.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/identity.py src/neurocvguard/rules.py src/neurocvguard/checks src/neurocvguard/_projection.py tests/conftest.py tests/test_cohort_inventory.py tests/test_identity.py tests/test_cohort_checks.py qa/evidence/S03/run_check.py` | 0 |
| [mypy-second](mypy-second.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [lint-initial](lint-initial.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [lint-import-fix](lint-import-fix.json) | `.venv/Scripts/python.exe -m ruff check --select I --fix src/neurocvguard/_projection.py src/neurocvguard/checks/cohort.py src/neurocvguard/identity.py src/neurocvguard/rules.py tests/test_cohort_checks.py tests/test_identity.py` | 0 |
| [format-refinements](format-refinements.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/_projection.py src/neurocvguard/checks/cohort.py src/neurocvguard/identity.py src/neurocvguard/rules.py tests/test_identity.py` | 0 |
| [format-final-sources](format-final-sources.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/checks/cohort.py tests/test_cohort_checks.py tests/test_identity.py qa/evidence/S03` | 0 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S03/pytest-final.xml` | 0 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [lint-final](lint-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [install-ordinary](install-ordinary.json) | `.venv-install/Scripts/python.exe -m pip install .` | 1 |
| [install-ordinary-retry](install-ordinary-retry.json) | `.venv-install/Scripts/python.exe -m pip install .` | 0 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 1 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard --junitxml=qa/evidence/S03/doctests.xml` | 0 |
| [format-doc-example](format-doc-example.json) | `.venv/Scripts/python.exe -m ruff format docs/cohort_checks.md` | 0 |
| [installed-smoke](installed-smoke.json) | `.venv-install/Scripts/python.exe qa/evidence/S03/check_installed.py` | 0 |
| [format-passed](format-passed.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [documented-example-final](documented-example-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_cohort_checks.py::test_documented_synthetic_example` | 0 |
| [environment](environment.json) | `.venv/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 |
| [installed-pip-check](installed-pip-check.json) | `.venv-install/Scripts/python.exe -m pip check` | 0 |
| [installed-environment](installed-environment.json) | `.venv-install/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 |
| [closeout-format](closeout-format.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [closeout-preservation](closeout-preservation.json) | `.venv/Scripts/python.exe qa/evidence/S03/check_closeout.py` | 0 |
