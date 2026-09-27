# S15 recorded commands

Exact argument vectors, environments, timestamps and outputs are in the linked JSON.
Failed attempts are retained; later correction does not change their exit status.

| Record | Exit | Command argument vector |
|---|---:|---|
| [adversarial-corrected.json](adversarial-corrected.json) | 1 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_hardening.py", "--junitxml=qa/evidence/S15/adversarial-corrected.xml"]` |
| [adversarial-final.json](adversarial-final.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_hardening.py", "--junitxml=qa/evidence/S15/adversarial-final.xml"]` |
| [adversarial.json](adversarial.json) | 1 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_hardening.py", "--junitxml=qa/evidence/S15/adversarial.xml"]` |
| [benchmarks.json](benchmarks.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/benchmark.py"]` |
| [boundary-regressions-corrected.json](boundary-regressions-corrected.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_hardening.py", "-k", "remote or collision"]` |
| [boundary-regressions.json](boundary-regressions.json) | 1 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_hardening.py", "-k", "remote or collision"]` |
| [cold-rng.json](cold-rng.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/cold_rng.py"]` |
| [coverage-baseline.json](coverage-baseline.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "--cov=neurocvguard", "--cov-branch", "--cov-report=json:qa/evidence/S15/coverage-baseline-data.json", "--cov-report=term-missing", "--junitxml=qa/evidence/S15/baseline.xml"]` |
| [coverage-gate-check.json](coverage-gate-check.json) | 1 | `[".venv/Scripts/python.exe", "qa/evidence/S15/check_coverage.py"]` |
| [coverage-gate-verified.json](coverage-gate-verified.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/check_coverage.py"]` |
| [diff-check.json](diff-check.json) | 0 | `["git", "diff", "--check"]` |
| [docs.json](docs.json) | 0 | `[".venv/Scripts/python.exe", "-m", "sphinx", "-E", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]` |
| [doctests.json](doctests.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "--doctest-modules", "src/neurocvguard"]` |
| [final-0.json](final-0.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/run_shard.py", "0"]` |
| [final-1.json](final-1.json) | 1 | `[".venv/Scripts/python.exe", "qa/evidence/S15/run_shard.py", "1"]` |
| [final-2.json](final-2.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/run_shard.py", "2"]` |
| [final-3.json](final-3.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/run_shard.py", "3"]` |
| [format-close.json](format-close.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]` |
| [format-final.json](format-final.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]` |
| [format.json](format.json) | 1 | `[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]` |
| [hardening-and-affected.json](hardening-and-affected.json) | 1 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_hardening.py", "tests/test_config.py", "tests/test_input_guards.py", "tests/test_plan_exports.py", "tests/test_report_projection.py", "tests/test_comparison.py", "tests/test_comparison_cli.py", "--junitxml=qa/evidence/S15/hardening-and-affected.xml"]` |
| [import-probe-restored.json](import-probe-restored.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_bootstrap.py::test_import_has_no_side_effects", "--cov=neurocvguard", "--cov-branch", "--cov-report=", "--junitxml=qa/evidence/S15/import-probe-restored.xml"]` |
| [lint-close.json](lint-close.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]` |
| [lint-final.json](lint-final.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]` |
| [lint.json](lint.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]` |
| [mutations.json](mutations.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/mutations.py"]` |
| [path-message-regression.json](path-message-regression.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_plan_exports.py::test_output_validation"]` |
| [security-record-check.json](security-record-check.json) | 0 | `[".venv/Scripts/python.exe", "-c", "import json; d=json.load(open(\"qa/evidence/S15/security-inventory.json\")); assert not d[\"prohibited_call_hits\"] and not d[\"workflows\"]; assert all(x[\"license_files\"] for x in d[\"dependencies\"].values()); print(len(d[\"runtime_imports\"]), \"runtime imports;\", len(d[\"dependencies\"]), \"dependency license records; no listed unsafe calls or executable workflows\")"]` |
| [types-final.json](types-final.json) | 0 | `[".venv/Scripts/python.exe", "-m", "mypy", "src/neurocvguard"]` |
| [types.json](types.json) | 0 | `[".venv/Scripts/python.exe", "-m", "mypy", "src/neurocvguard"]` |
| [verified-0.json](verified-0.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/run_shard.py", "0"]` |
| [verified-1.json](verified-1.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/run_shard.py", "1"]` |
| [verified-2.json](verified-2.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/run_shard.py", "2"]` |
| [verified-3.json](verified-3.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/run_shard.py", "3"]` |
| [final-record-validation.json](final-record-validation.json) | 0 | `[".venv/Scripts/python.exe", "qa/evidence/S15/finalize.py"]` |
| [final-diff-check.json](final-diff-check.json) | 0 | `["git", "diff", "--check"]` |
| [foundation-record-consistency.json](foundation-record-consistency.json) | 1 | `[".venv/Scripts/python.exe", "tools/validate_foundation.py"]` |
| [foundation-baseline-scope.json](foundation-baseline-scope.json) | 0 | `[".venv/Scripts/python.exe", "-c", "import hashlib,json; from pathlib import Path; b=json.loads(Path(\"qa/evidence/S14/baseline.json\").read_text()); names=[\"tools/validate_foundation.py\",\"fixtures/manifest.json\"]; assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==b[\"files\"][p] for p in names); native={str(p) for p in Path(\"contracts\").glob(\"*.schema.json\")}; key=json.loads(Path(\"fixtures/manifest.json\").read_text())[0][\"schema\"]; assert key not in native and key.replace(\"/\",chr(92)) in native; print(\"Validator and fixture manifest match entry revision; native Windows keys disagree with manifest forward-slash keys. Validator also explicitly requires all application stages NOT_STARTED, so it is a frozen-foundation check, not an implemented-stage gate.\")"]` |
| [validator-artifacts.json](validator-artifacts.json) | 0 | `[".venv/Scripts/python.exe", "tools/validate_foundation.py", "--mode", "artifacts", "--output", "qa/evidence/S15/artifacts-consistency.json"]` |
| [validator-followup-docs.json](validator-followup-docs.json) | 0 | `[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]` |
| [validator-followup-format.json](validator-followup-format.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]` |
| [validator-followup-lint.json](validator-followup-lint.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]` |
| [validator-followup-tests-corrected.json](validator-followup-tests-corrected.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_foundation_validator.py", "--junitxml=qa/evidence/S15/validator-followup-tests-corrected.xml"]` |
| [validator-followup-tests-final.json](validator-followup-tests-final.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_foundation_validator.py", "--junitxml=qa/evidence/S15/validator-followup-tests-final.xml"]` |
| [validator-followup-tests.json](validator-followup-tests.json) | 1 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_foundation_validator.py", "--junitxml=qa/evidence/S15/validator-followup-tests.xml"]` |
| [validator-foundation.json](validator-foundation.json) | 1 | `[".venv/Scripts/python.exe", "tools/validate_foundation.py", "--output", "qa/evidence/S15/foundation-snapshot-check.json"]` |
