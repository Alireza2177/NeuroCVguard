# S05 recorded command attempts

All checks ran from the project root. Logs contain exact argument vectors, UTC
start, recorder/platform details, UTF-8 override, exit code and complete
privacy-normalized stdout/stderr. Commands below use POSIX-style quoting solely
to render the argument vector; subprocess runs directly without a shell.

Invocation: `python qa/evidence/S05/run_check.py <record-name> <command ...>`.
Record-name is the linked filename without .json. Failed attempts are retained;
overlapping test counts are not additive.

| UTC start | Recorded command | Exit | Log |
|---|---|---|---|
| 2026-09-13T10:51:26.331290+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_generation.py` | 0 | [s05a-participants.json](s05a-participants.json) |
| 2026-09-13T10:52:02.248785+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 1 | [lint-initial.json](lint-initial.json) |
| 2026-09-13T10:52:02.375875+00:00 | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 | [mypy-initial.json](mypy-initial.json) |
| 2026-09-13T10:54:01.948090+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_domain_generation.py` | 0 | [s05b-domains.json](s05b-domains.json) |
| 2026-09-13T10:54:35.219636+00:00 | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/splitting.py src/neurocvguard/models.py src/neurocvguard/errors.py src/neurocvguard/serialization.py tests/test_generation.py tests/test_domain_generation.py` | 0 | [format-current.json](format-current.json) |
| 2026-09-13T10:58:26.190273+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_plan_exports.py` | 1 | [s05c-exports.json](s05c-exports.json) |
| 2026-09-13T10:59:07.977590+00:00 | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/io.py src/neurocvguard/models.py src/neurocvguard/splitting.py src/neurocvguard/rules.py src/neurocvguard/_projection.py src/neurocvguard/__init__.py tests/test_plan_exports.py` | 0 | [format-s05c.json](format-s05c.json) |
| 2026-09-13T10:59:10.308078+00:00 | `.venv/Scripts/python.exe -m ruff check --fix src/neurocvguard/splitting.py src/neurocvguard/rules.py src/neurocvguard/io.py src/neurocvguard/_projection.py tests/test_generation.py tests/test_domain_generation.py tests/test_plan_exports.py` | 1 | [lint-fixes.json](lint-fixes.json) |
| 2026-09-13T11:00:10.802659+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_plan_exports.py` | 0 | [s05c-exports-fixed.json](s05c-exports-fixed.json) |
| 2026-09-13T11:00:51.326747+00:00 | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 | [mypy-second.json](mypy-second.json) |
| 2026-09-13T11:00:52.777197+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 1 | [lint-second.json](lint-second.json) |
| 2026-09-13T11:00:54.523524+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config` | 0 | [regression-initial.json](regression-initial.json) |
| 2026-09-13T11:04:01.232775+00:00 | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/splitting.py src/neurocvguard/io.py src/neurocvguard/rules.py tests/test_generation.py tests/test_plan_exports.py docs/split_generation.md` | 0 | [format-docs-tests.json](format-docs-tests.json) |
| 2026-09-13T11:04:03.987512+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_generation.py::test_insufficient_class_components_can_retain_valid_warning_plan tests/test_generation.py::test_splitter_infeasibility_is_not_input_error_or_fallback tests/test_plan_exports.py::test_no_overwrite_race_preserves_competing_file tests/test_plan_exports.py::test_staging_failure_does_not_replace_existing_artifacts tests/test_plan_exports.py::test_documented_planning_example` | 0 | [s05-edges.json](s05-edges.json) |
| 2026-09-13T11:05:06.980911+00:00 | `.venv/Scripts/python.exe -m ruff format qa/evidence/S05/check_closeout.py qa/evidence/S05/check_installed.py` | 0 | [format-helpers.json](format-helpers.json) |
| 2026-09-13T11:05:09.463752+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S05/pytest-final.xml` | 0 | [pytest-final.json](pytest-final.json) |
| 2026-09-13T11:05:11.246561+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 1 | [lint-final.json](lint-final.json) |
| 2026-09-13T11:05:13.150916+00:00 | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 | [mypy-final.json](mypy-final.json) |
| 2026-09-13T11:05:15.190714+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 | [doctests.json](doctests.json) |
| 2026-09-13T11:05:16.942006+00:00 | `.venv-install/Scripts/python.exe -m pip install .` | 1 | [install-ordinary.json](install-ordinary.json) |
| 2026-09-13T11:05:37.612804+00:00 | `.venv-install/Scripts/python.exe -m pip install .` | 0 | [install-ordinary-retry.json](install-ordinary-retry.json) |
| 2026-09-13T11:06:11.535825+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 0 | [lint-passed.json](lint-passed.json) |
| 2026-09-13T11:06:13.295550+00:00 | `.venv-install/Scripts/python.exe qa/evidence/S05/check_installed.py` | 0 | [installed-smoke.json](installed-smoke.json) |
| 2026-09-13T11:06:14.992007+00:00 | `.venv-install/Scripts/python.exe -m pip check` | 0 | [pip-check.json](pip-check.json) |
| 2026-09-13T11:06:16.932876+00:00 | `.venv/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 | [environment-dev.json](environment-dev.json) |
| 2026-09-13T11:06:18.766779+00:00 | `.venv-install/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 | [environment-ordinary.json](environment-ordinary.json) |
| 2026-09-13T11:09:59.211969+00:00 | `.venv/Scripts/python.exe -m ruff format --check .` | 0 | [format-final.json](format-final.json) |
| 2026-09-13T11:10:41.976314+00:00 | `.venv/Scripts/python.exe qa/evidence/S05/check_closeout.py` | 0 | [closeout-preservation.json](closeout-preservation.json) |
| 2026-09-13T11:11:16.125380+00:00 | `.venv/Scripts/python.exe -m ruff format --check .` | 0 | [closeout-format.json](closeout-format.json) |
| 2026-09-13T11:11:17.602007+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 0 | [closeout-lint.json](closeout-lint.json) |
