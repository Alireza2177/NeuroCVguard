# S17 exact command ledger

Commands are argument vectors; full output, cwd and environment are in each JSON.
Exit 3 in the initial preflight is an expected blocked gate, not a passing release.
Historical failures are retained. Public API/link/hash observations are separate evidence.

## recorder-error.json

Recorded start: see record. Exit: 1.

```json
[".venv/Scripts/python.exe", "qa/evidence/S17/run_check.py", "namespaces", ".venv/Scripts/python.exe", "qa/evidence/S17/check_namespaces.py"]
```

## checkpoint-tests.json

Recorded start: 2026-09-27T05:30:23.588201+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_release_preflight.py", "tests/test_distribution_audit.py", "--junitxml=qa/evidence/S17/checkpoint-tests.xml"]
```

## preflight-command.json

Recorded start: 2026-09-27T05:30:36.659836+00:00. Exit: 3.

```json
[".venv/Scripts/python.exe", "tools/release_preflight.py", "--dist", "dist/s16", "--output", "qa/evidence/S17/preflight.json"]
```

## archive-command.json

Recorded start: 2026-09-27T05:30:38.224317+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/audit_distributions.py", "--dist", "dist/s16", "--output", "qa/evidence/S17/distributions.json"]
```

## lint.json

Recorded start: 2026-09-27T05:33:05.337715+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]
```

## format.json

Recorded start: 2026-09-27T05:33:06.841514+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]
```

## types.json

Recorded start: 2026-09-27T05:33:08.494268+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "mypy", "src/neurocvguard"]
```

## docs.json

Recorded start: 2026-09-27T05:33:10.273632+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]
```

## documentation-tests.json

Recorded start: 2026-09-27T05:33:12.129337+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_documentation.py", "-k", "local_markdown_links or metadata_and_human_review", "--junitxml=qa/evidence/S17/documentation-tests.xml"]
```

## artifacts-consistency.json

Recorded start: 2026-09-27T05:35:20.605684+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/validate_foundation.py", "--mode", "artifacts", "--output", "qa/evidence/S17/artifacts-data.json"]
```

## diff-check.json

Recorded start: 2026-09-27T05:35:22.082622+00:00. Exit: 0.

```json
["git", "diff", "--check"]
```

## ci-wheel-local.json

Recorded start: 2026-09-27T05:40:15.305068+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/ci_wheel_check.py", "--dist", "dist/s16", "--out", "<TEMP>\\neurocvguard-s17-ci-check"]
```

## ci-lint.json

Recorded start: 2026-09-27T05:41:36.429173+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]
```

## ci-format.json

Recorded start: 2026-09-27T05:41:38.163608+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]
```

## ci-docs.json

Recorded start: 2026-09-27T05:41:40.073664+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]
```

## owner-metadata-tests.json

Recorded start: 2026-09-27T05:46:57.096541+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_distribution_audit.py", "tests/test_release_preflight.py", "tests/test_documentation.py", "-k", "not quickstart_commands_verbatim and not documented_subcommands_help", "--junitxml=qa/evidence/S17/owner-metadata-tests.xml"]
```

## owner-build.json

Recorded start: 2026-09-27T05:48:48.474231+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "build", "--outdir", "dist/s17-owner-candidate"]
```

## release-tools-tests.json

Recorded start: 2026-09-27T05:50:23.767272+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_release_assets.py", "tests/test_release_preflight.py", "tests/test_distribution_audit.py", "--junitxml=qa/evidence/S17/release-tools-tests.xml"]
```

## candidate-build.json

Recorded start: 2026-09-27T05:51:50.018723+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "build", "--outdir", "dist/s17-candidate"]
```

## candidate-audit.json

Recorded start: 2026-09-27T05:52:54.973881+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/audit_distributions.py", "--dist", "dist/s17-candidate", "--output", "qa/evidence/S17/candidate-distributions.json"]
```

## candidate-wheel.json

Recorded start: 2026-09-27T05:53:13.572813+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/ci_wheel_check.py", "--dist", "dist/s17-candidate", "--out", "<TEMP>\\neurocvguard-s17-final-check"]
```

## candidate-lint.json

Recorded start: 2026-09-27T05:54:32.487903+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]
```

## candidate-format.json

Recorded start: 2026-09-27T05:54:34.196353+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]
```

## candidate-docs.json

Recorded start: 2026-09-27T05:54:36.030035+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]
```

## candidate-files.json

Recorded start: 2026-09-27T05:54:38.011093+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/verify_release_assets.py", "--manifest", "state/release/0.1.0-artifacts.json", "--dist", "dist/s17-candidate"]
```

## candidate-full-suite.json

Recorded start: 2026-09-27T05:58:26.119562+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "--junitxml=qa/evidence/S17/candidate-full-suite.xml"]
```

## candidate-docs-final.json

Recorded start: 2026-09-27T06:01:05.009225+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]
```

## authorized-preflight.json

Recorded start: 2026-09-27T06:08:16.034058+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/release_preflight.py", "--manifest", "state/release/0.1.0-artifacts.json", "--dist", "dist/s17-candidate", "--output", "qa/evidence/S17/authorized-preflight-data.json"]
```

## citation-honesty-tests.json

Recorded start: 2026-09-27T06:29:29.526176+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_documentation.py", "-k", "local_markdown_links or metadata_and_human_review"]
```

## citation-docs.json

Recorded start: 2026-09-27T06:31:47.945133+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]
```

## citation-format.json

Recorded start: 2026-09-27T06:35:07.641544+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]
```

## public-wheel-install.json

Recorded start: 2026-09-27T06:37:50.767957+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/ci_wheel_check.py", "--dist", "dist/s17-pypi-public", "--out", "<TEMP>/neurocvguard-s17-public-check"]
```

## public-index-resolution.json

Recorded start: 2026-09-27T06:39:18.168457+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pip", "download", "--no-deps", "--only-binary=:all:", "--index-url", "https://pypi.org/simple", "neurocvguard==0.1.0", "--dest", "dist/s17-index-download"]
```

## final-documentation-tests.json

Recorded start: 2026-09-27T06:45:04.040922+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_documentation.py"]
```

## final-lint.json

Recorded start: 2026-09-27T06:45:24.454479+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]
```

## final-format.json

Recorded start: 2026-09-27T06:45:26.136190+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]
```

## final-docs.json

Recorded start: 2026-09-27T06:45:27.875315+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]
```

## final-diff-check.json

Recorded start: 2026-09-27T06:46:05.432622+00:00. Exit: 0.

```json
["git", "diff", "--check"]
```

## post-release-docs-push.json

Recorded start: 2026-09-27T06:46:44.440217+00:00. Exit: 0.

```json
["git", "push", "origin", "HEAD:main"]
```

## final-artifacts.json

Recorded start: 2026-09-27T06:48:04.696572+00:00. Exit: 0.

```json
[".venv/Scripts/python.exe", "tools/validate_foundation.py", "--mode", "artifacts"]
```
