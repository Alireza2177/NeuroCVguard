# S11 command evidence

Exact argument vectors, exit codes, environment and outputs are in each record.

| Evidence | Command | Exit |
|---|---|---:|
| [s11a-inner-plans](s11a-inner-plans.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_inner_plans.py tests/test_evaluation_preflight.py` | 1 |
| [s11a-corrected](s11a-corrected.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_inner_plans.py tests/test_evaluation_preflight.py` | 0 |
| [s11b-candidates](s11b-candidates.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_nested_candidates.py tests/test_evaluation_fits.py` | 0 |
| [s11c-nested-runner](s11c-nested-runner.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_nested_runner.py tests/test_evaluation_runner.py` | 0 |
| [s11c-cli](s11c-cli.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_nested_cli.py tests/test_evaluation_cli.py` | 0 |
| [format-apply](format-apply.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/_inner_plans.py src/neurocvguard/_tuning.py src/neurocvguard/_evaluation_inputs.py src/neurocvguard/_evaluation_fits.py src/neurocvguard/evaluation.py tests/test_inner_plans.py tests/test_nested_candidates.py tests/test_nested_runner.py tests/test_nested_cli.py tests/test_evaluation_preflight.py qa/evidence/S11` | 0 |
| [lint-initial](lint-initial.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [mypy-initial](mypy-initial.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [lint-fix](lint-fix.json) | `.venv/Scripts/python.exe -m ruff check --fix src/neurocvguard/_evaluation_inputs.py src/neurocvguard/_tuning.py` | 0 |
| [format-followup](format-followup.json) | `.venv/Scripts/python.exe -m ruff format tests/test_inner_plans.py tests/test_evaluation_preflight.py qa/evidence/S11/run_evaluation.py` | 0 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S11/pytest-final.xml` | 0 |
| [journey-editable](journey-editable.json) | `.venv/Scripts/python.exe -I qa/evidence/S11/run_evaluation.py` | 0 |
| [environment](environment.json) | `.venv/Scripts/python.exe -m pip list --format=json` | 0 |
| [install-ordinary](install-ordinary.json) | `.venv-install/Scripts/python.exe -m pip install --no-build-isolation --no-deps .` | 0 |
| [journey-ordinary](journey-ordinary.json) | `.venv-install/Scripts/python.exe -I qa/evidence/S11/run_evaluation.py --ordinary` | 0 |
| [environment-ordinary](environment-ordinary.json) | `.venv-install/Scripts/python.exe -m pip list --format=json` | 0 |
| [lint-final](lint-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 1 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 |
| [format-docs-and-descriptions](format-docs-and-descriptions.json) | `.venv/Scripts/python.exe -m ruff format docs/evaluation.md src/neurocvguard/__init__.py src/neurocvguard/_projection.py src/neurocvguard/cli.py src/neurocvguard/splitting.py` | 0 |
| [format-final-corrected](format-final-corrected.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 1 |
| [diff-whitespace](diff-whitespace.json) | `git diff --check` | 0 |
| [format-evidence-helper](format-evidence-helper.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S11/close_stage.py` | 0 |
| [format-verified](format-verified.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [docs-example](docs-example.json) | `.venv/Scripts/python.exe -c "import re; from pathlib import Path; source=Path(\"docs/evaluation.md\").read_text(encoding=\"utf-8\"); blocks=re.findall(r\"```python\n(.*?)```\",source,re.S); scope={}; [exec(compile(code,\"docs/evaluation.md\",\"exec\"),scope) for code in blocks]; print(\"Both documented Python examples passed; nested result completed.\")"` | 0 |
| [stage-finish](stage-finish.json) | `python qa/evidence/S11/close_stage.py finish` | 0 |
| [preservation](preservation.json) | `python qa/evidence/S11/close_stage.py verify` | 0 |
| [handoff-format](handoff-format.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [handoff-lint](handoff-lint.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
