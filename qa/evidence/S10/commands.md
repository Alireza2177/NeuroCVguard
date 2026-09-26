# S10 command evidence

Exact argument vectors, exit codes, environment and outputs are in each record.

| Evidence | Command | Exit |
|---|---|---:|
| [s10a-preflight](s10a-preflight.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_evaluation_preflight.py` | 2 |
| [s10a-corrected](s10a-corrected.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_evaluation_preflight.py` | 0 |
| [s10b-fits](s10b-fits.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_evaluation_fits.py` | 0 |
| [contract-extension](contract-extension.json) | `python qa/evidence/S10/extend_contract.py` | 0 |
| [s10c-metrics-runner](s10c-metrics-runner.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_evaluation_metrics.py tests/test_evaluation_runner.py` | 0 |
| [s10c-cli](s10c-cli.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_evaluation_cli.py tests/test_cli_commands.py tests/test_report_rendering.py` | 0 |
| [formatting](formatting.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/_evaluation_inputs.py src/neurocvguard/_evaluation_fits.py src/neurocvguard/evaluation.py src/neurocvguard/metrics.py src/neurocvguard/models.py src/neurocvguard/rules.py src/neurocvguard/_projection.py src/neurocvguard/reporting.py src/neurocvguard/cli.py src/neurocvguard/__init__.py tests/test_evaluation_preflight.py tests/test_evaluation_fits.py tests/test_evaluation_metrics.py tests/test_evaluation_runner.py tests/test_evaluation_cli.py tests/test_cli_commands.py qa/evidence/S10` | 0 |
| [mypy-initial](mypy-initial.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 |
| [lint-initial](lint-initial.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [imports-fix](imports-fix.json) | `.venv/Scripts/python.exe -m ruff check --select I --fix src/neurocvguard/_evaluation_fits.py tests/test_evaluation_preflight.py tests/test_evaluation_fits.py tests/test_evaluation_metrics.py tests/test_evaluation_runner.py tests/test_evaluation_cli.py` | 0 |
| [contract-migration](contract-migration.json) | `.venv/Scripts/python.exe qa/evidence/S10/check_contract.py` | 0 |
| [journey-editable](journey-editable.json) | `.venv/Scripts/python.exe -I qa/evidence/S10/run_evaluation.py` | 1 |
| [format-ready](format-ready.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/evaluation.py src/neurocvguard/_projection.py src/neurocvguard/_evaluation_inputs.py src/neurocvguard/_evaluation_fits.py src/neurocvguard/cli.py src/neurocvguard/reporting.py src/neurocvguard/rules.py tests/test_evaluation_runner.py tests/test_evaluation_cli.py tests/test_evaluation_fits.py qa/evidence/S10` | 0 |
| [lint-ready](lint-ready.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [mypy-ready](mypy-ready.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [pytest-initial](pytest-initial.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config` | 0 |
| [journey-corrected](journey-corrected.json) | `.venv/Scripts/python.exe -I qa/evidence/S10/run_evaluation.py` | 0 |
| [projection-regression](projection-regression.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_evaluation_cli.py tests/test_report_projection.py tests/test_report_rendering.py` | 0 |
| [install-ordinary](install-ordinary.json) | `.venv-install/Scripts/python.exe -m pip install .` | 1 |
| [install-ordinary-retry](install-ordinary-retry.json) | `.venv-install/Scripts/python.exe -m pip install .` | 1 |
| [install-build-backend](install-build-backend.json) | `.venv-install/Scripts/python.exe -m pip install hatchling` | 0 |
| [install-ordinary-offline](install-ordinary-offline.json) | `.venv-install/Scripts/python.exe -m pip install --no-build-isolation --no-deps .` | 0 |
| [format-final-source](format-final-source.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/_projection.py src/neurocvguard/_evaluation_inputs.py tests/test_evaluation_preflight.py tests/test_evaluation_cli.py qa/evidence/S10/check_contract.py` | 0 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S10/pytest-final.xml` | 0 |
| [lint-final](lint-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [journey-ordinary](journey-ordinary.json) | `.venv-install/Scripts/python.exe -I qa/evidence/S10/run_evaluation.py --ordinary` | 0 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 |
| [environment](environment.json) | `.venv/Scripts/python.exe -m pip list --format=json` | 0 |
| [environment-ordinary](environment-ordinary.json) | `.venv-install/Scripts/python.exe -m pip list --format=json` | 0 |
| [closeout-map](closeout-map.json) | `python qa/evidence/S10/close_stage.py finish` | 0 |
| [regenerate-reading-copies](regenerate-reading-copies.json) | `.venv/Scripts/python.exe tools/build_master.py` | 0 |
| [preservation](preservation.json) | `python qa/evidence/S10/close_stage.py verify` | 0 |
| [diff-check](diff-check.json) | `git diff --check` | 0 |
