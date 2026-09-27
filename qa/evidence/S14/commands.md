# S14 recorded commands

Exact argument vectors, environments, timestamps and outputs are in the linked JSON.
Failed attempts are retained; later correction does not change their exit status.

| Record | Exit | Command argument vector |
|---|---:|---|
| [all-guide-examples.json](all-guide-examples.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_documentation.py", "--junitxml=qa/evidence/S14/all-guide-examples.xml"]` |
| [docs-first.json](docs-first.json) | 1 | `[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]` |
| [docs-second.json](docs-second.json) | 0 | `[".venv/Scripts/python.exe", "-m", "sphinx", "-E", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html"]` |
| [documentation-tests.json](documentation-tests.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_documentation.py", "--junitxml=qa/evidence/S14/documentation.xml"]` |
| [external-links.json](external-links.json) | 1 | `[".venv/Scripts/python.exe", "-m", "sphinx", "-W", "--keep-going", "-b", "linkcheck", "docs", "docs/_build/linkcheck"]` |
| [format.json](format.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "format", "--check", "."]` |
| [lint.json](lint.json) | 0 | `[".venv/Scripts/python.exe", "-m", "ruff", "check", "."]` |
| [regression.json](regression.json) | 0 | `[".venv/Scripts/python.exe", "-m", "pytest", "-q", "--strict-markers", "--strict-config", "tests/test_config.py", "tests/test_contracts.py", "tests/test_cli_commands.py", "tests/test_examples.py", "--junitxml=qa/evidence/S14/regression.xml"]` |
| [types.json](types.json) | 0 | `[".venv/Scripts/python.exe", "-m", "mypy", "src/neurocvguard"]` |
