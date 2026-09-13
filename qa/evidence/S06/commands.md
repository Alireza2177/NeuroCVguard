# S06 exact command register

All commands ran from the project root in PowerShell. The recorder runs
the displayed argument vector without a child shell, sets PYTHONIOENCODING=utf-8,
and retains stdout/stderr, actual timestamps, recorder Python and platform.
Each record name is exclusive; initial failures are retained. Commands below
include the recorder invocation for direct reproduction with a fresh record name.

| Exact command | Exit | Evidence |
|---|---:|---|
| `python qa/evidence/S06/run_check.py s06a-pairs .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_association_pairs.py` | 0 | [s06a-pairs.json](s06a-pairs.json) |
| `python qa/evidence/S06/run_check.py s06b-statistics .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_association_statistics.py` | 0 | [s06b-statistics.json](s06b-statistics.json) |
| `python qa/evidence/S06/run_check.py s06c-checks .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_association_checks.py` | 0 | [s06c-checks.json](s06c-checks.json) |
| `python qa/evidence/S06/run_check.py format-apply .venv/Scripts/python.exe -m ruff format src/neurocvguard/checks/associations.py src/neurocvguard/_projection.py src/neurocvguard/rules.py tests/test_association_pairs.py tests/test_association_statistics.py tests/test_association_checks.py` | 0 | [format-apply.json](format-apply.json) |
| `python qa/evidence/S06/run_check.py mypy-initial .venv/Scripts/python.exe -m mypy src/neurocvguard` | 1 | [mypy-initial.json](mypy-initial.json) |
| `python qa/evidence/S06/run_check.py lint-initial .venv/Scripts/python.exe -m ruff check .` | 1 | [lint-initial.json](lint-initial.json) |
| `python qa/evidence/S06/run_check.py imports-fix .venv/Scripts/python.exe -m ruff check --select I --fix tests/test_association_statistics.py` | 0 | [imports-fix.json](imports-fix.json) |
| `python qa/evidence/S06/run_check.py format-followup .venv/Scripts/python.exe -m ruff format tests/test_association_checks.py src/neurocvguard/rules.py` | 0 | [format-followup.json](format-followup.json) |
| `python qa/evidence/S06/run_check.py s06c-final .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_association_checks.py` | 0 | [s06c-final.json](s06c-final.json) |
| `python qa/evidence/S06/run_check.py pytest-final .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --junitxml=qa/evidence/S06/pytest-final.xml` | 0 | [pytest-final.json](pytest-final.json) |
| `python qa/evidence/S06/run_check.py mypy-final .venv/Scripts/python.exe -m mypy src/neurocvguard` | 0 | [mypy-final.json](mypy-final.json) |
| `python qa/evidence/S06/run_check.py environment-dev .venv/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 | [environment-dev.json](environment-dev.json) |
| `python qa/evidence/S06/run_check.py install-ordinary .venv-install/Scripts/python.exe -m pip install .` | 1 | [install-ordinary.json](install-ordinary.json) |
| `python qa/evidence/S06/run_check.py helpers-format .venv/Scripts/python.exe -m ruff format qa/evidence/S06/check_installed.py qa/evidence/S06/check_closeout.py` | 0 | [helpers-format.json](helpers-format.json) |
| `python qa/evidence/S06/run_check.py install-ordinary-retry .venv-install/Scripts/python.exe -m pip install .` | 0 | [install-ordinary-retry.json](install-ordinary-retry.json) |
| `python qa/evidence/S06/run_check.py installed-smoke .venv-install/Scripts/python.exe qa/evidence/S06/check_installed.py` | 0 | [installed-smoke.json](installed-smoke.json) |
| `python qa/evidence/S06/run_check.py lint-passed .venv/Scripts/python.exe -m ruff check .` | 0 | [lint-passed.json](lint-passed.json) |
| `python qa/evidence/S06/run_check.py format-final .venv/Scripts/python.exe -m ruff format --check .` | 1 | [format-final.json](format-final.json) |
| `python qa/evidence/S06/run_check.py doctests .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config --doctest-modules src/neurocvguard` | 0 | [doctests.json](doctests.json) |
| `python qa/evidence/S06/run_check.py environment-installed .venv-install/Scripts/python.exe qa/evidence/S00/environment_probe.py` | 0 | [environment-installed.json](environment-installed.json) |
| `python qa/evidence/S06/run_check.py guide-format .venv/Scripts/python.exe -m ruff format docs/association_diagnostics.md` | 0 | [guide-format.json](guide-format.json) |
| `python qa/evidence/S06/run_check.py format-passed .venv/Scripts/python.exe -m ruff format --check .` | 0 | [format-passed.json](format-passed.json) |
| `python qa/evidence/S06/run_check.py guide-final .venv/Scripts/python.exe -m pytest -q --strict-markers --strict-config tests/test_association_checks.py::test_documented_association_example` | 0 | [guide-final.json](guide-final.json) |
| `python qa/evidence/S06/run_check.py lint-final .venv/Scripts/python.exe -m ruff check .` | 0 | [lint-final.json](lint-final.json) |
| `python qa/evidence/S06/run_check.py closeout .venv/Scripts/python.exe qa/evidence/S06/check_closeout.py` | 0 | [closeout.json](closeout.json) |

Full environment details: environment-dev.json and environment-installed.json.
Ordinary installation first failed to obtain hatchling within the restricted sandbox;
install-ordinary-retry used approved escalation and succeeded in the existing isolated
project environment. No dependency version was changed by that install.

Preservation: closeout.json records 356 baseline files retained, 347 unchanged and
9 authorized modifications; no non-S06 status or prior evidence was altered.
JUnit hostname was replaced by <LOCAL_HOST>; outcomes and counts were not changed.
The baseline excludes virtual environments, caches, bytecode and build outputs.

Exploratory Git status returned exit 1 (not a Git repository). A mistyped test file
read was corrected through a directory inventory; neither was a verification pass.
The final inventory covers local source/docs/evidence, not installed environment files.
No human review, CI or later-stage execution is inferred.
