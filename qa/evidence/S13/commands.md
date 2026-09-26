# S13 command evidence

Exact argument vectors, exit codes, environment and outputs are in each record.

| Evidence | Command | Exit |
|---|---|---:|
| [s13a-generators](s13a-generators.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_synthetic.py` | 0 |
| [demo-smoke](demo-smoke.json) | `.venv/Scripts/python.exe -m neurocvguard demo --out qa/evidence/S13/smoke-clean` | 2 |
| [static-initial](static-initial.json) | `.venv/Scripts/python.exe -m ruff check src/neurocvguard/demo.py src/neurocvguard/synthetic.py src/neurocvguard/cli.py tests/test_synthetic.py examples` | 1 |
| [demo-smoke-corrected](demo-smoke-corrected.json) | `.venv/Scripts/python.exe -m neurocvguard demo --out qa/evidence/S13/smoke-clean` | 0 |
| [format-initial](format-initial.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/demo.py src/neurocvguard/synthetic.py src/neurocvguard/cli.py src/neurocvguard/_projection.py src/neurocvguard/reporting.py tests/test_synthetic.py examples qa/evidence/S13/*.py` | 0 |
| [imports-fix](imports-fix.json) | `.venv/Scripts/python.exe -m ruff check --select I,F401 --fix src/neurocvguard/demo.py src/neurocvguard/synthetic.py src/neurocvguard/cli.py tests/test_synthetic.py examples` | 0 |
| [mypy-initial](mypy-initial.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 |
| [mypy-corrected](mypy-corrected.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [s13b-workflows](s13b-workflows.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_demo.py tests/test_examples.py tests/test_cli_commands.py tests/test_report_projection.py tests/test_report_rendering.py` | 0 |
| [format-b](format-b.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/demo.py src/neurocvguard/synthetic.py src/neurocvguard/cli.py tests/test_demo.py tests/test_examples.py tests/test_cli_commands.py` | 0 |
| [lint-b](lint-b.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [imports-fix-b](imports-fix-b.json) | `.venv/Scripts/python.exe -m ruff check --select I,F401 --fix tests/test_demo.py tests/test_examples.py src/neurocvguard/demo.py` | 0 |
| [executed-examples](executed-examples.json) | `.venv/Scripts/python.exe qa/evidence/S13/capture_examples.py` | 0 |
| [ordinary-install](ordinary-install.json) | `.venv-install/Scripts/python.exe -m pip install --no-build-isolation --no-deps .` | 0 |
| [installed-journey](installed-journey.json) | `.venv-install/Scripts/python.exe qa/evidence/S13/installed_journey.py` | 0 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S13/pytest-final.xml` | 0 |
| [format-c](format-c.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/cli.py src/neurocvguard/demo.py qa/evidence/S13/capture_examples.py qa/evidence/S13/installed_journey.py` | 0 |
| [lint-integration](lint-integration.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [evidence-format](evidence-format.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S13/close_stage.py qa/evidence/S13/check_captured.py` | 0 |
| [lint-final](lint-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 |
| [format-evidence-final](format-evidence-final.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S13/close_stage.py qa/evidence/S13/check_captured.py` | 0 |
| [lint-verified](lint-verified.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [format-verified](format-verified.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [captured-integrity](captured-integrity.json) | `.venv/Scripts/python.exe qa/evidence/S13/check_captured.py` | 1 |
| [captured-integrity-corrected](captured-integrity-corrected.json) | `.venv/Scripts/python.exe qa/evidence/S13/check_captured.py` | 0 |
| [diff-check](diff-check.json) | `git diff --check` | 0 |
| [evidence-style-final](evidence-style-final.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S13/check_captured.py` | 0 |
| [format-close](format-close.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [evidence-lint](evidence-lint.json) | `.venv/Scripts/python.exe -m ruff check qa/evidence/S13/check_captured.py` | 0 |
| [stage-record](stage-record.json) | `.venv/Scripts/python.exe qa/evidence/S13/close_stage.py finish` | 0 |
| [preservation](preservation.json) | `.venv/Scripts/python.exe qa/evidence/S13/close_stage.py verify` | 1 |
| [registration-repair](registration-repair.json) | `.venv/Scripts/python.exe qa/evidence/S13/repair_stage_registration.py` | 0 |
| [preservation-corrected](preservation-corrected.json) | `.venv/Scripts/python.exe qa/evidence/S13/close_stage.py verify` | 0 |
| [registration-format](registration-format.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S13/prepare_stage.py qa/evidence/S13/repair_stage_registration.py` | 0 |
| [registration-lint](registration-lint.json) | `.venv/Scripts/python.exe -m ruff check qa/evidence/S13/prepare_stage.py qa/evidence/S13/repair_stage_registration.py` | 0 |
| [stage-approved](stage-approved.json) | `.venv/Scripts/python.exe qa/evidence/S13/close_stage.py finish` | 0 |
| [preservation-approved](preservation-approved.json) | `.venv/Scripts/python.exe qa/evidence/S13/close_stage.py verify` | 0 |
