# S01 recorded commands

Exact argument vectors are preserved in each linked JSON file, with UTC time,
working directory, environment overrides, exit code and captured output.
All commands ran locally on Windows. Failed intermediate attempts remain visible.
Paths in captured output are privacy-normalized. No shell was used by the recorder.

| Evidence | Exact command (PowerShell quoting) | Exit code |
|---|---|---|
| [s01a-config](s01a-config.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_config.py` | 0 |
| [install-type-stubs](install-type-stubs.json) | `.venv/Scripts/python.exe -m pip install pandas-stubs types-jsonschema` | 1 |
| [install-type-stubs-retry](install-type-stubs-retry.json) | `.venv/Scripts/python.exe -m pip install pandas-stubs types-jsonschema` | 0 |
| [mypy-initial](mypy-initial.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 |
| [s01b-contracts](s01b-contracts.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_contracts.py` | 1 |
| [s01b-contracts-fixed](s01b-contracts-fixed.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_contracts.py tests/test_config.py` | 0 |
| [mypy-second](mypy-second.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 |
| [lint-initial](lint-initial.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [lint-fix](lint-fix.json) | `.venv/Scripts/python.exe -m ruff check --select I,F --fix src/neurocvguard tests/test_config.py tests/test_contracts.py qa/evidence/S01` | 0 |
| [format-fix](format-fix.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard tests/test_config.py tests/test_contracts.py qa/evidence/S01 pyproject.toml` | 0 |
| [lint-after-format](lint-after-format.json) | `.venv/Scripts/python.exe -m ruff check . --output-format concise` | 1 |
| [format-edges](format-edges.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard tests/test_contract_edges.py` | 0 |
| [edges](edges.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_contract_edges.py` | 0 |
| [formatting-finalize](formatting-finalize.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard tests/test_config.py tests/test_contracts.py tests/test_contract_edges.py qa/evidence/S01 pyproject.toml` | 0 |
| [import-order-finalize](import-order-finalize.json) | `.venv/Scripts/python.exe -m ruff check --select I --fix src/neurocvguard tests/test_config.py tests/test_contracts.py tests/test_contract_edges.py qa/evidence/S01` | 0 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S01/pytest-final.xml` | 0 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [ruff-final](ruff-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard --junitxml=qa/evidence/S01/doctests.xml` | 0 |
| [install-editable-final](install-editable-final.json) | `.venv/Scripts/python.exe -m pip install -e .[dev,docs]` | 0 |
| [install-ordinary-final](install-ordinary-final.json) | `.venv-install/Scripts/python.exe -m pip install .` | 0 |
| [installed-resources](installed-resources.json) | `.venv-install/Scripts/python.exe qa/evidence/S01/check_installed.py` | 0 |
| [ruff-passed](ruff-passed.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [format-passed](format-passed.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [environment-final](environment-final.json) | `.venv/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 |
| [pip-check](pip-check.json) | `.venv/Scripts/python.exe -m pip check` | 0 |
| [closeout-preservation](closeout-preservation.json) | `.venv/Scripts/python.exe qa/evidence/S01/check_closeout.py` | 0 |
| [closeout-format-helper](closeout-format-helper.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S01/check_closeout.py` | 0 |
| [closeout-lint](closeout-lint.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [closeout-format](closeout-format.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 1 |
| [closeout-format-runner](closeout-format-runner.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S01/run_check.py` | 0 |
| [closeout-format-passed](closeout-format-passed.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
