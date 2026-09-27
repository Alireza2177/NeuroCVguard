# S16 exact command index

Argument vectors below are JSON arrays, not shell command strings. Paths use the
same normalization as the original record. Each linked JSON contains cwd, actual
environment, exit code and complete captured output. Initial failures are retained.
Wrapper logs for matrix/final-install scripts also contain each nested command.
Local setup paths are internal evidence, not public-release metadata.

## archive-final

Record: [archive-final.json](archive-final.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/audit_distributions.py", "--dist", "dist/s16", "--output", "qa/evidence/S16/distributions.json"]
```

Working directory: `<PROJECT_ROOT>`.

## archive-initial

Record: [archive-initial.json](archive-initial.json). Exit: 1.

```json
[".venv/Scripts/python.exe", "tools/audit_distributions.py", "--dist", "dist/s16-initial", "--output", "qa/evidence/S16/archive-initial-data.json"]
```

Working directory: `<PROJECT_ROOT>`.

## build-final

Record: [build-final.json](build-final.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "build", "--outdir", "dist/s16"]
```

Working directory: `<PROJECT_ROOT>`.

## build-first

Record: [build-first.json](build-first.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "build", "--outdir", "dist/s16-initial"]
```

Working directory: `<PROJECT_ROOT>`.

## diff-check

Record: [diff-check.json](diff-check.json). Exit: 0.

```json
["git", "diff", "--check"]
```

Working directory: `<PROJECT_ROOT>`.

## distribution-tests-final

Record: [distribution-tests-final.json](distribution-tests-final.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_distribution_audit.py", "--junitxml=qa/evidence/S16/distribution-tests-final.xml"]
```

Working directory: `<PROJECT_ROOT>`.

## distribution-tests

Record: [distribution-tests.json](distribution-tests.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_distribution_audit.py", "--junitxml=qa/evidence/S16/distribution-tests.xml"]
```

Working directory: `<PROJECT_ROOT>`.

## docs

Record: [docs.json](docs.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]
```

Working directory: `<PROJECT_ROOT>`.

## finalize

Record: [finalize.json](finalize.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "qa/evidence/S16/finalize.py"]
```

Working directory: `<PROJECT_ROOT>`.

## format-close

Record: [format-close.json](format-close.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]
```

Working directory: `<PROJECT_ROOT>`.

## format

Record: [format.json](format.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]
```

Working directory: `<PROJECT_ROOT>`.

## host-python-matrix

Record: [host-python-matrix.json](host-python-matrix.json). Exit: 0.

```json
["py", "-0p"]
```

Working directory: `<PROJECT_ROOT>`.

## lint-close

Record: [lint-close.json](lint-close.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]
```

Working directory: `<PROJECT_ROOT>`.

## lint-final

Record: [lint-final.json](lint-final.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]
```

Working directory: `<PROJECT_ROOT>`.

## lint

Record: [lint.json](lint.json). Exit: 1.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]
```

Working directory: `<PROJECT_ROOT>`.

## linux-311-environment

Record: [linux-311-environment.json](linux-311-environment.json). Exit: 0.

```json
["<LINUX_WORK>/linux-311/bin/python", "-m", "pip", "list", "--format=json"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-311-install

Record: [linux-311-install.json](linux-311-install.json). Exit: 0.

```json
["<PROJECT_ROOT>/dist/s16-tooling/uv-linux", "pip", "install", "--python", "<LINUX_WORK>/linux-311/bin/python", "-e", "<LINUX_WORK>/source[dev,docs]"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-311-packaging

Record: [linux-311-packaging.json](linux-311-packaging.json). Exit: 0.

```json
["<LINUX_WORK>/linux-311/bin/python", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_distribution_audit.py", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/linux-311-packaging.xml"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-311-tests

Record: [linux-311-tests.json](linux-311-tests.json). Exit: 0.

```json
["<LINUX_WORK>/linux-311/bin/python", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/linux-311.xml"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-311-venv

Record: [linux-311-venv.json](linux-311-venv.json). Exit: 0.

```json
["<PROJECT_ROOT>/dist/s16-tooling/uv-linux", "venv", "--seed", "--python", "<LINUX_WORK>/pythons/cpython-3.11.16-linux-x86_64-gnu/bin/python3.11", "<LINUX_WORK>/linux-311"]
```

Working directory: `<LINUX_WORK>`.

## linux-312-environment

Record: [linux-312-environment.json](linux-312-environment.json). Exit: 0.

```json
["<LINUX_WORK>/linux-312/bin/python", "-m", "pip", "list", "--format=json"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-312-install

Record: [linux-312-install.json](linux-312-install.json). Exit: 0.

```json
["<PROJECT_ROOT>/dist/s16-tooling/uv-linux", "pip", "install", "--python", "<LINUX_WORK>/linux-312/bin/python", "-e", "<LINUX_WORK>/source[dev,docs]"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-312-packaging

Record: [linux-312-packaging.json](linux-312-packaging.json). Exit: 0.

```json
["<LINUX_WORK>/linux-312/bin/python", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_distribution_audit.py", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/linux-312-packaging.xml"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-312-tests

Record: [linux-312-tests.json](linux-312-tests.json). Exit: 0.

```json
["<LINUX_WORK>/linux-312/bin/python", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/linux-312.xml"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-312-venv

Record: [linux-312-venv.json](linux-312-venv.json). Exit: 0.

```json
["<PROJECT_ROOT>/dist/s16-tooling/uv-linux", "venv", "--seed", "--python", "<LINUX_WORK>/pythons/cpython-3.12.14-linux-x86_64-gnu/bin/python3.12", "<LINUX_WORK>/linux-312"]
```

Working directory: `<LINUX_WORK>`.

## linux-313-environment

Record: [linux-313-environment.json](linux-313-environment.json). Exit: 0.

```json
["<LINUX_WORK>/linux-313/bin/python", "-m", "pip", "list", "--format=json"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-313-install

Record: [linux-313-install.json](linux-313-install.json). Exit: 0.

```json
["<PROJECT_ROOT>/dist/s16-tooling/uv-linux", "pip", "install", "--python", "<LINUX_WORK>/linux-313/bin/python", "-e", "<LINUX_WORK>/source[dev,docs]"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-313-packaging

Record: [linux-313-packaging.json](linux-313-packaging.json). Exit: 0.

```json
["<LINUX_WORK>/linux-313/bin/python", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_distribution_audit.py", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/linux-313-packaging.xml"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-313-tests

Record: [linux-313-tests.json](linux-313-tests.json). Exit: 0.

```json
["<LINUX_WORK>/linux-313/bin/python", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/linux-313.xml"]
```

Working directory: `<LINUX_WORK>/source`.

## linux-313-venv

Record: [linux-313-venv.json](linux-313-venv.json). Exit: 0.

```json
["<PROJECT_ROOT>/dist/s16-tooling/uv-linux", "venv", "--seed", "--python", "<LINUX_WORK>/pythons/cpython-3.13.15-linux-x86_64-gnu/bin/python3.13", "<LINUX_WORK>/linux-313"]
```

Working directory: `<LINUX_WORK>`.

## linux-final-install

Record: [linux-final-install.json](linux-final-install.json). Exit: 0.

```json
["wsl", "-d", "Ubuntu", "--", "python3", "/mnt/c/Users/Alireza217/Desktop/NeuroCVguard_Foundation_v1.0.0/qa/evidence/S16/final_install.py"]
```

Working directory: `<PROJECT_ROOT>`.

## linux-matrix

Record: [linux-matrix.json](linux-matrix.json). Exit: 0.

```json
["wsl", "-d", "Ubuntu", "--", "python3", "/mnt/c/Users/Alireza217/Desktop/NeuroCVguard_Foundation_v1.0.0/qa/evidence/S16/linux_matrix.py"]
```

Working directory: `<PROJECT_ROOT>`.

## linux-packaging-matrix

Record: [linux-packaging-matrix.json](linux-packaging-matrix.json). Exit: 0.

```json
["wsl", "-d", "Ubuntu", "--", "python3", "/mnt/c/Users/Alireza217/Desktop/NeuroCVguard_Foundation_v1.0.0/qa/evidence/S16/linux_supplement.py"]
```

Working directory: `<PROJECT_ROOT>`.

## linux-python-install

Record: [linux-python-install.json](linux-python-install.json). Exit: 0.

```json
["wsl", "-d", "Ubuntu", "--", "/mnt/c/Users/Alireza217/Desktop/NeuroCVguard_Foundation_v1.0.0/dist/s16-tooling/uv-linux", "python", "install", "3.11", "3.12", "3.13", "--no-bin", "--install-dir", "/tmp/neurocvguard-s16-0azxjcue/pythons"]
```

Working directory: `<PROJECT_ROOT>`.

## linux-python-persistent

Record: [linux-python-persistent.json](linux-python-persistent.json). Exit: 0.

```json
["wsl", "-d", "Ubuntu", "--", "/mnt/c/Users/Alireza217/Desktop/NeuroCVguard_Foundation_v1.0.0/dist/s16-tooling/uv-linux", "python", "install", "3.11", "3.12", "3.13", "--no-bin", "--install-dir", "/var/tmp/neurocvguard-s16-0azxjcue/pythons"]
```

Working directory: `<PROJECT_ROOT>`.

## linux-uv-download

Record: [linux-uv-download.json](linux-uv-download.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pip", "download", "--only-binary=:all:", "--no-deps", "--platform", "manylinux_2_17_x86_64", "--dest", "dist/s16-tooling", "uv"]
```

Working directory: `<PROJECT_ROOT>`.

## metadata-final

Record: [metadata-final.json](metadata-final.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "twine", "check", "--strict", "dist/s16/neurocvguard-0.1.0-py3-none-any.whl", "dist/s16/neurocvguard-0.1.0.tar.gz"]
```

Working directory: `<PROJECT_ROOT>`.

## metadata-first

Record: [metadata-first.json](metadata-first.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "twine", "check", "--strict", "dist/s16-initial/neurocvguard-0.1.0-py3-none-any.whl", "dist/s16-initial/neurocvguard-0.1.0.tar.gz"]
```

Working directory: `<PROJECT_ROOT>`.

## minimum-catalog-corrected

Record: [minimum-catalog-corrected.json](minimum-catalog-corrected.json). Exit: 0.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/minimum311/Scripts/python.exe", "-I", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_association_checks.py::test_rules_match_normative_catalog", "tests/test_cohort_checks.py::test_rule_registry_exactly_matches_normative_catalog", "tests/test_evaluation_runner.py::test_s10_rule_catalog_metadata", "tests/test_plan_exports.py::test_plan_catalog_matches_normative_definitions", "tests/test_preprocessing.py::test_event_order_invariance_and_registry", "tests/test_split_audit.py::test_split_rules_match_normative_catalog", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/minimum-catalog-corrected.xml"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue\minimum311-checks`.

## minimum-final-install

Record: [minimum-final-install.json](minimum-final-install.json). Exit: 0.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/minimum311/Scripts/python.exe", "-m", "pip", "install", "--no-index", "--no-deps", "--force-reinstall", "<TEMP>\\neurocvguard-s16-0azxjcue/neurocvguard-0.1.0-py3-none-any.whl"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue`.

## minimum-final-probe

Record: [minimum-final-probe.json](minimum-final-probe.json). Exit: 0.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/minimum311/Scripts/python.exe", "-I", "<TEMP>\\neurocvguard-s16-0azxjcue/verify_final_wheel.py", "--forbid-root", "<PROJECT_ROOT>", "--wheel", "<TEMP>\\neurocvguard-s16-0azxjcue/neurocvguard-0.1.0-py3-none-any.whl", "--out", "<TEMP>\\neurocvguard-s16-0azxjcue/minimum-final-demo"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue`.

## minimum-install

Record: [minimum-install.json](minimum-install.json). Exit: 0.

```json
["uv", "pip", "install", "--python", "<TEMP>\\neurocvguard-s16-0azxjcue/minimum311/Scripts/python.exe", "dist/s16-initial/neurocvguard-0.1.0-py3-none-any.whl", "numpy==1.26.4", "pandas==2.2.3", "scipy==1.13.1", "scikit-learn==1.5.2", "Jinja2==3.1.6", "jsonschema==4.23.0", "pytest", "hypothesis"]
```

Working directory: `<PROJECT_ROOT>`.

## minimum-pip-check

Record: [minimum-pip-check.json](minimum-pip-check.json). Exit: 0.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/minimum311/Scripts/python.exe", "-m", "pip", "check"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue`.

## minimum-tests

Record: [minimum-tests.json](minimum-tests.json). Exit: 1.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/minimum311/Scripts/python.exe", "-I", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "<TEMP>\\neurocvguard-s16-0azxjcue/minimum311-checks/tests", "--ignore=<TEMP>\\neurocvguard-s16-0azxjcue/minimum311-checks/tests/test_documentation.py", "--ignore=<TEMP>\\neurocvguard-s16-0azxjcue/minimum311-checks/tests/test_foundation_validator.py", "--deselect=test_bootstrap.py::test_editable_install_points_to_source", "--junitxml=qa/evidence/S16/minimum-tests.xml"]
```

Working directory: `<PROJECT_ROOT>`.

## prepare-linux-persistent

Record: [prepare-linux-persistent.json](prepare-linux-persistent.json). Exit: 0.

```json
["wsl", "-d", "Ubuntu", "--", "python3", "/mnt/c/Users/Alireza217/Desktop/NeuroCVguard_Foundation_v1.0.0/qa/evidence/S16/prepare_matrix.py"]
```

Working directory: `<PROJECT_ROOT>`.

## prepare-linux

Record: [prepare-linux.json](prepare-linux.json). Exit: 1.

```json
["wsl", "-d", "Ubuntu", "--", "python3", "/mnt/c/Users/Alireza217/Desktop/NeuroCVguard_Foundation_v1.0.0/qa/evidence/S16/prepare_matrix.py"]
```

Working directory: `<PROJECT_ROOT>`.

## prepare-windows

Record: [prepare-windows.json](prepare-windows.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "qa/evidence/S16/prepare_matrix.py"]
```

Working directory: `<PROJECT_ROOT>`.

## privacy-scan

Record: [privacy-scan.json](privacy-scan.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "qa/evidence/S16/privacy_scan.py"]
```

Working directory: `<PROJECT_ROOT>`.

## types

Record: [types.json](types.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "mypy", "src/neurocvguard"]
```

Working directory: `<PROJECT_ROOT>`.

## windows-catalog-corrected

Record: [windows-catalog-corrected.json](windows-catalog-corrected.json). Exit: 0.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/Scripts/python.exe", "-I", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_association_checks.py::test_rules_match_normative_catalog", "tests/test_cohort_checks.py::test_rule_registry_exactly_matches_normative_catalog", "tests/test_evaluation_runner.py::test_s10_rule_catalog_metadata", "tests/test_plan_exports.py::test_plan_catalog_matches_normative_definitions", "tests/test_preprocessing.py::test_event_order_invariance_and_registry", "tests/test_split_audit.py::test_split_rules_match_normative_catalog", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/windows-catalog-corrected.xml"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue\wheel312-checks`.

## windows-final-install

Record: [windows-final-install.json](windows-final-install.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "qa/evidence/S16/final_install.py"]
```

Working directory: `<PROJECT_ROOT>`.

## windows-minimum-venv

Record: [windows-minimum-venv.json](windows-minimum-venv.json). Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "venv", "<TEMP>\\neurocvguard-s16-0azxjcue/minimum311"]
```

Working directory: `<PROJECT_ROOT>`.

## windows-wheel-core

Record: [windows-wheel-core.json](windows-wheel-core.json). Exit: 1.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/Scripts/python.exe", "-I", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests", "--ignore=tests/test_documentation.py", "--ignore=tests/test_foundation_validator.py", "--deselect=tests/test_bootstrap.py::test_editable_install_points_to_source", "--junitxml=<PROJECT_ROOT>/qa/evidence/S16/windows-wheel-core.xml"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue\wheel312-checks`.

## windows-wheel-corrected-probe

Record: [windows-wheel-corrected-probe.json](windows-wheel-corrected-probe.json). Exit: 0.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/Scripts/python.exe", "-I", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/verify_wheel.py", "--forbid-root", "<PROJECT_ROOT>", "--out", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312-corrected-demo"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue`.

## windows-wheel-install

Record: [windows-wheel-install.json](windows-wheel-install.json). Exit: 0.

```json
["uv", "pip", "install", "--python", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/Scripts/python.exe", "dist/s16-initial/neurocvguard-0.1.0-py3-none-any.whl", "pytest", "hypothesis"]
```

Working directory: `<PROJECT_ROOT>`.

## windows-wheel-offline

Record: [windows-wheel-offline.json](windows-wheel-offline.json). Exit: 1.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/Scripts/python.exe", "-I", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/verify_wheel.py", "--forbid-root", "<PROJECT_ROOT>", "--out", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312-demo"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue`.

## windows-wheel-probe-debug

Record: [windows-wheel-probe-debug.json](windows-wheel-probe-debug.json). Exit: 1.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/Scripts/python.exe", "-I", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/verify_wheel.py", "--forbid-root", "<PROJECT_ROOT>", "--out", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312-demo"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue`.

## windows-wheel-probe-external

Record: [windows-wheel-probe-external.json](windows-wheel-probe-external.json). Exit: 1.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/Scripts/python.exe", "-I", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/verify_wheel.py", "--forbid-root", "<PROJECT_ROOT>", "--out", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312-demo"]
```

Working directory: `<USER_HOME>\AppData\Local\Temp\neurocvguard-s16-0azxjcue`.

## windows-wheel-probe

Record: [windows-wheel-probe.json](windows-wheel-probe.json). Exit: 1.

```json
["<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/Scripts/python.exe", "-I", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312/verify_wheel.py", "--forbid-root", "<PROJECT_ROOT>", "--out", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312-demo"]
```

Working directory: `<PROJECT_ROOT>`.

## windows-wheel-venv

Record: [windows-wheel-venv.json](windows-wheel-venv.json). Exit: 0.

```json
["py", "-3.12", "-m", "venv", "<TEMP>\\neurocvguard-s16-0azxjcue/wheel312"]
```

Working directory: `<PROJECT_ROOT>`.

## wsl-probe

Record: [wsl-probe.json](wsl-probe.json). Exit: 0.

```json
["wsl", "-d", "Ubuntu", "--", "python3", "--version"]
```

Working directory: `<PROJECT_ROOT>`.
