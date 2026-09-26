# S08 exact command evidence

Commands were run from the project root through the S08 recorder. Each JSON
contains the exact argument vector, exit code, timestamp, platform and output.
Paths/usernames are normalized. Failures are retained alongside corrections.

| Evidence | Exact checked command | Exit |
|---|---|---:|
| [s08a-projection](s08a-projection.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_report_projection.py tests/test_association_checks.py tests/test_contracts.py tests/test_contract_edges.py` | 0 |
| [s08b-rendering](s08b-rendering.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_report_rendering.py` | 1 |
| [s08b-corrected](s08b-corrected.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_report_rendering.py` | 0 |
| [s08c-security](s08c-security.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_report_security.py` | 0 |
| [imports-fix](imports-fix.json) | `.venv/Scripts/python.exe -m ruff check --select I,F401 --fix src/neurocvguard/reporting.py src/neurocvguard/_report_writes.py src/neurocvguard/_report_tables.py src/neurocvguard/_projection.py src/neurocvguard/rules.py src/neurocvguard/__init__.py tests/test_report_projection.py tests/test_report_rendering.py tests/test_report_security.py` | 0 |
| [format-apply](format-apply.json) | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/reporting.py src/neurocvguard/_report_writes.py src/neurocvguard/_report_tables.py src/neurocvguard/_projection.py src/neurocvguard/rules.py src/neurocvguard/__init__.py tests/test_report_projection.py tests/test_report_rendering.py tests/test_report_security.py` | 0 |
| [mypy-initial](mypy-initial.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 |
| [lint-initial](lint-initial.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [render-fixtures](render-fixtures.json) | `.venv/Scripts/python.exe qa/evidence/S08/render_fixtures.py` | 0 |
| [format-refine](format-refine.json) | `.venv/Scripts/python.exe -m ruff format src tests qa/evidence/S08` | 0 |
| [mypy-refine](mypy-refine.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 |
| [install-ordinary](install-ordinary.json) | `.venv-install/Scripts/python.exe -m pip install .` | 1 |
| [install-ordinary-retry](install-ordinary-retry.json) | `.venv-install/Scripts/python.exe -m pip install .` | 0 |
| [format-complete](format-complete.json) | `.venv/Scripts/python.exe -m ruff format src tests qa/evidence/S08` | 0 |
| [pytest-final](pytest-final.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S08/pytest-final.xml` | 1 |
| [build-assets](build-assets.json) | `.venv/Scripts/python.exe -m build --outdir qa/evidence/S08/dist` | 1 |
| [build-assets-retry](build-assets-retry.json) | `.venv/Scripts/python.exe -m build --outdir qa/evidence/S08/dist` | 0 |
| [mypy-final](mypy-final.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [doctests](doctests.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 |
| [environment-dev](environment-dev.json) | `.venv/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 |
| [installed-smoke](installed-smoke.json) | `.venv-install/Scripts/python.exe qa/evidence/S08/check_installed.py` | 0 |
| [packaged-assets](packaged-assets.json) | `.venv/Scripts/python.exe qa/evidence/S08/check_assets.py` | 0 |
| [environment-installed](environment-installed.json) | `.venv-install/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 |
| [final-fixture-focus](final-fixture-focus.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_report_projection.py::test_path_and_email_target_labels_are_not_public tests/test_report_security.py::test_at_s08_06_html_injection` | 0 |
| [pytest-final-corrected](pytest-final-corrected.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S08/pytest-final-corrected.xml` | 0 |
| [projection-rerender](projection-rerender.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_report_projection.py tests/test_report_rendering.py` | 0 |
| [format-closeout](format-closeout.json) | `.venv/Scripts/python.exe -m ruff format src tests qa/evidence/S08` | 0 |
| [mypy-verified](mypy-verified.json) | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 |
| [lint-verified](lint-verified.json) | `.venv/Scripts/python.exe -m ruff check .` | 1 |
| [pytest-verified](pytest-verified.json) | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S08/pytest-verified.xml` | 0 |
| [build-final](build-final.json) | `.venv/Scripts/python.exe -m build --outdir qa/evidence/S08/dist-final` | 0 |
| [format-evidence](format-evidence.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S08` | 0 |
| [lint-final](lint-final.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [format-final](format-final.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 1 |
| [packaged-final](packaged-final.json) | `.venv/Scripts/python.exe qa/evidence/S08/check_assets.py dist-final` | 0 |
| [install-final-wheel](install-final-wheel.json) | `.venv-install/Scripts/python.exe -m pip install --no-index --no-deps --force-reinstall qa/evidence/S08/dist-final/neurocvguard-0.1.0-py3-none-any.whl` | 0 |
| [format-guide](format-guide.json) | `.venv/Scripts/python.exe -m ruff format docs/reporting.md` | 0 |
| [format-verified](format-verified.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 1 |
| [installed-verified](installed-verified.json) | `.venv-install/Scripts/python.exe qa/evidence/S08/check_installed.py` | 0 |
| [rendered-final](rendered-final.json) | `.venv-install/Scripts/python.exe qa/evidence/S08/check_rendered.py` | 1 |
| [imports-evidence](imports-evidence.json) | `.venv/Scripts/python.exe -m ruff check qa/evidence/S08 --select I --fix` | 0 |
| [format-helpers](format-helpers.json) | `.venv/Scripts/python.exe -m ruff format qa/evidence/S08` | 0 |
| [format-completed](format-completed.json) | `.venv/Scripts/python.exe -m ruff format --check .` | 0 |
| [rendered-verified](rendered-verified.json) | `.venv-install/Scripts/python.exe qa/evidence/S08/check_rendered.py` | 0 |
| [lint-completed](lint-completed.json) | `.venv/Scripts/python.exe -m ruff check .` | 0 |
| [map-closeout](map-closeout.json) | `.venv/Scripts/python.exe qa/evidence/S08/finalize_evidence.py map` | 0 |
| [closeout](closeout.json) | `.venv/Scripts/python.exe qa/evidence/S08/check_closeout.py` | 0 |
| [final-diff-check](final-diff-check.json) | `git diff --check` | 2 |
| [diff-verified](diff-verified.json) | `git diff --check` | 0 |
