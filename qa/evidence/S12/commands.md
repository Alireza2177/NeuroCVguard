# S12 command evidence

Exact argument vectors, exit codes, environment and outputs are in each record.

| Evidence | Command | Exit |
|---|---|---:|
| [schema-extension](schema-extension.json) | `.venv/Scripts/python.exe qa/evidence/S12/extend_context.py` | 0 |
| [s12a-comparison](s12a-comparison.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_comparison.py tests/test_contracts.py tests/test_report_projection.py` | 1 |
| [s12a-corrected](s12a-corrected.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_comparison.py tests/test_contracts.py tests/test_report_projection.py` | 0 |
| [s12b-diagnostics](s12b-diagnostics.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_diagnostic_evaluation.py tests/test_evaluation_preflight.py tests/test_nested_runner.py` | 0 |
| [context-migration](context-migration.json) | `.venv/Scripts/python.exe qa/evidence/S12/check_context.py` | 0 |
| [reading-copies](reading-copies.json) | `.venv/Scripts/python.exe tools/build_master.py` | 0 |
| [format-a-b](format-a-b.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/comparison.py src/neurocvguard/_diagnostics.py src/neurocvguard/_evaluation_inputs.py src/neurocvguard/evaluation.py src/neurocvguard/models.py src/neurocvguard/__init__.py src/neurocvguard/_projection.py src/neurocvguard/rules.py tests/test_comparison.py tests/test_diagnostic_evaluation.py tests/test_evaluation_preflight.py qa/evidence/S12` | 0 |
| [lint-a-b](lint-a-b.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [mypy-a-b](mypy-a-b.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [lint-fix-a-b](lint-fix-a-b.json) | `.venv/Scripts/python.exe -m ruff check --fix src/neurocvguard/_evaluation_inputs.py src/neurocvguard/_projection.py tests/test_comparison.py tests/test_diagnostic_evaluation.py` | 0 |
| [format-fix-a-b](format-fix-a-b.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/models.py src/neurocvguard/rules.py qa/evidence/S12/check_context.py` | 0 |
| [s12c-cli-report](s12c-cli-report.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_comparison_cli.py tests/test_cli_commands.py tests/test_report_rendering.py tests/test_report_projection.py` | 1 |
| [s12c-corrected](s12c-corrected.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_comparison_cli.py tests/test_cli_commands.py tests/test_report_rendering.py tests/test_report_projection.py` | 0 |
| [ordinary-install](ordinary-install.json) | `.venv-install/Scripts/python.exe -m pip install --no-build-isolation --no-deps .` | 0 |
| [format-c](format-c.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard tests/test_comparison_cli.py tests/test_report_rendering.py qa/evidence/S12` | 0 |
| [lint-c](lint-c.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S12/pytest-final.xml` | 0 |
| [lint-fix-c](lint-fix-c.json) | `.venv/Scripts/python.exe -m ruff check --select I --fix tests/test_comparison_cli.py` | 0 |
| [format-c-final](format-c-final.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/cli.py tests/test_comparison.py tests/test_comparison_cli.py` | 0 |
| [editable-journey](editable-journey.json) | `.venv/Scripts/python.exe qa/evidence/S12/run_comparison.py` | 0 |
| [ordinary-journey](ordinary-journey.json) | `.venv-install/Scripts/python.exe qa/evidence/S12/run_comparison.py --ordinary` | 0 |
| [lint-final](lint-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [format-verified](format-verified.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 1 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 |
| [format-line-endings](format-line-endings.json) | `.venv/Scripts/python.exe -m ruff format tests/test_cli_commands.py qa/evidence/S12/close_stage.py` | 0 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [format-evidence](format-evidence.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S12/close_stage.py` | 0 |
| [diff-check](diff-check.json) | `git diff --check` | 0 |
| [evidence-style](evidence-style.json) | `.venv/Scripts/python.exe -m ruff check qa/evidence/S12/close_stage.py` | 0 |
| [stage-finish](stage-finish.json) | `.venv/Scripts/python.exe qa/evidence/S12/close_stage.py finish` | 0 |
| [preservation](preservation.json) | `.venv/Scripts/python.exe qa/evidence/S12/close_stage.py verify` | 0 |
