# S04 recorded command attempts

All recorded checks ran from the project root. Each JSON log contains the exact
argument vector, UTC start time, recorder/platform details, UTF-8 override, exit
code and complete privacy-normalized stdout/stderr. The command column below uses
POSIX-style quoting only as a readable rendering of the argument vector; the
runner calls subprocess directly without a shell.

Invocation: `python qa/evidence/S04/run_check.py <record-name> <command ...>`.
The prefix is identical for every record; record-name is the filename without .json.
Failed attempts are retained. Overlapping test runs are not additive.

| UTC start | Exact recorded command | Exit | Log |
|---|---|---|---|
| 2026-09-13T08:33:34.161175+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_split_io.py` | 1 | [s04a-import.json](s04a-import.json) |
| 2026-09-13T08:33:53.202364+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_split_io.py` | 0 | [s04a-import-fixed.json](s04a-import-fixed.json) |
| 2026-09-13T08:38:09.149685+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_partitions.py` | 0 | [s04b-outer.json](s04b-outer.json) |
| 2026-09-13T08:44:17.729413+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_split_audit.py` | 0 | [s04c-nested.json](s04c-nested.json) |
| 2026-09-13T08:44:39.705330+00:00 | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/io.py src/neurocvguard/audit.py src/neurocvguard/checks/partitions.py src/neurocvguard/rules.py src/neurocvguard/_projection.py src/neurocvguard/__init__.py tests/test_split_io.py tests/test_partitions.py tests/test_split_audit.py qa/evidence/S04/run_check.py` | 0 | [format-source.json](format-source.json) |
| 2026-09-13T08:44:42.803734+00:00 | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 | [mypy-initial.json](mypy-initial.json) |
| 2026-09-13T08:44:44.223185+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config` | 0 | [regression-initial.json](regression-initial.json) |
| 2026-09-13T08:44:46.084316+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 1 | [lint-initial.json](lint-initial.json) |
| 2026-09-13T08:45:45.028858+00:00 | `.venv/Scripts/python.exe -m ruff check --select I --fix src/neurocvguard tests/test_partitions.py tests/test_split_audit.py tests/test_split_io.py` | 0 | [lint-import-fix.json](lint-import-fix.json) |
| 2026-09-13T08:45:47.014805+00:00 | `.venv/Scripts/python.exe -m ruff format src/neurocvguard tests/test_partitions.py tests/test_split_audit.py tests/test_split_io.py` | 0 | [format-fixes.json](format-fixes.json) |
| 2026-09-13T08:46:16.836641+00:00 | `.venv/Scripts/python.exe -m ruff format src/neurocvguard/checks/partitions.py src/neurocvguard/rules.py` | 0 | [format-literals.json](format-literals.json) |
| 2026-09-13T08:46:18.769526+00:00 | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 | [mypy-second.json](mypy-second.json) |
| 2026-09-13T08:46:20.220702+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 1 | [lint-second.json](lint-second.json) |
| 2026-09-13T08:48:03.617543+00:00 | `.venv/Scripts/python.exe -m ruff check --select UP034 --fix src/neurocvguard/io.py` | 0 | [lint-parentheses-fix.json](lint-parentheses-fix.json) |
| 2026-09-13T08:50:23.889027+00:00 | `.venv/Scripts/python.exe -m ruff format docs/split_audits.md tests/test_split_edges.py src/neurocvguard/io.py` | 0 | [format-example-and-edges.json](format-example-and-edges.json) |
| 2026-09-13T08:50:26.346054+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_split_edges.py` | 0 | [s04-edges.json](s04-edges.json) |
| 2026-09-13T08:53:46.087500+00:00 | `.venv/Scripts/python.exe -m ruff format qa/evidence/S04/check_closeout.py qa/evidence/S04/check_installed.py` | 0 | [format-helpers.json](format-helpers.json) |
| 2026-09-13T08:54:07.552243+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S04/pytest-final.xml` | 0 | [pytest-final.json](pytest-final.json) |
| 2026-09-13T08:54:09.206136+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 1 | [lint-final.json](lint-final.json) |
| 2026-09-13T08:54:10.976321+00:00 | `.venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 | [mypy-final.json](mypy-final.json) |
| 2026-09-13T08:54:12.489016+00:00 | `.venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 | [doctest-final.json](doctest-final.json) |
| 2026-09-13T08:54:14.247132+00:00 | `.venv-install/Scripts/python.exe -m pip install .` | 1 | [install-ordinary.json](install-ordinary.json) |
| 2026-09-13T09:00:01.402296+00:00 | `.venv-install/Scripts/python.exe -m pip install .` | 0 | [install-ordinary-retry.json](install-ordinary-retry.json) |
| 2026-09-13T09:00:15.737217+00:00 | `.venv/Scripts/python.exe -m ruff check --select I --fix tests/test_split_edges.py` | 0 | [lint-edges-fix.json](lint-edges-fix.json) |
| 2026-09-13T09:00:33.856232+00:00 | `.venv-install/Scripts/python.exe qa/evidence/S04/check_installed.py` | 0 | [installed-smoke.json](installed-smoke.json) |
| 2026-09-13T09:00:35.528669+00:00 | `.venv-install/Scripts/python.exe -m pip check` | 0 | [pip-check.json](pip-check.json) |
| 2026-09-13T09:00:37.284082+00:00 | `.venv/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 | [environment-dev.json](environment-dev.json) |
| 2026-09-13T09:00:38.915480+00:00 | `.venv-install/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 | [environment-ordinary.json](environment-ordinary.json) |
| 2026-09-13T09:01:18.210691+00:00 | `.venv/Scripts/python.exe -m ruff check .` | 0 | [lint-passed.json](lint-passed.json) |
| 2026-09-13T09:03:35.669742+00:00 | `.venv/Scripts/python.exe -m ruff format --check .` | 0 | [format-final.json](format-final.json) |
| 2026-09-13T09:04:00.198762+00:00 | `.venv/Scripts/python.exe qa/evidence/S04/check_closeout.py` | 0 | [closeout-preservation.json](closeout-preservation.json) |
| 2026-09-13T09:05:02.870197+00:00 | `.venv/Scripts/python.exe -m ruff format --check .` | 0 | [closeout-format.json](closeout-format.json) |
