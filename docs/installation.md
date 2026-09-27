# Installation and troubleshooting

Install [NeuroCVguard 0.1.0 from PyPI](https://pypi.org/project/neurocvguard/0.1.0/)
with Python 3.11 or newer. The S17 hosted matrix passed source tests and clean-wheel
checks on Linux Python 3.11/3.12/3.13, Windows/macOS 3.12 and the Python 3.11
direct-dependency floor. Earlier local Windows/WSL2 evidence is retained separately;
see [release evidence](release.md). These checks are not scientific certification.

Create a new environment (do not replace an unrelated one):

```text
python -m venv .venv
```

On Windows, use `.venv/Scripts/python.exe`; on Linux/macOS use
`.venv/bin/python`. The examples below call that interpreter `python` after you
activate the environment or substitute its full path:

```text
python -m pip install neurocvguard==0.1.0
python -m neurocvguard --version
python -m neurocvguard --help
```

For a source checkout, use `python -m pip install .`, or install development/docs
tools with `python -m pip install -e ".[dev,docs]"`. Initial
dependency installation needs an approved package registry or a prepared local
wheel cache. Runtime commands use local files only: no account, API key or GPU.
The development extra installs pytest, Hypothesis, coverage, Ruff, mypy and build
tools. The docs extra installs Sphinx/MyST. Do not install unrestricted user code
or deserialize models to use this package.

| Symptom | Repair |
|---|---|
| Import fails or console command is missing | Use the same environment's Python for installation and `python -m neurocvguard`. |
| Path contains spaces or Unicode | Quote each shell path; UTF-8 CSV/TSV and explicit `Path` objects are supported. |
| Unknown config key / duplicate JSON key | Compare with the configuration reference; use strict JSON, not comments or YAML. |
| Role missing or numeric ID | Map the actual column and preserve string identities upstream; do not guess or trim IDs. |
| Feature keys differ | Reconcile the explicit observation manifest; no row-order join or silent intersection. |
| Output exists | Choose a fresh directory or explicitly opt into `--overwrite` for named artifacts. |
| Resource limit exceeded | Review dimensions and memory first; raise only the relevant explicit guardrail. |
| Infeasible site split | Inspect crossing participants/protected components; document any upstream curation separately. |
| Fit failure / code 4 | Inspect retained incomplete records and convergence settings; do not average successful folds only. |

The tested direct-dependency floor is NumPy 1.26.4, pandas 2.2.3, SciPy 1.13.1,
scikit-learn 1.5.2, Jinja2 3.1.6 and jsonschema 4.23.0. These are conservative
tested lower bounds, not claims about the earliest usable versions. Exact floor
pins for Python 3.11 are in `requirements/minimum-py311.txt`; transitive versions
and commands are in the S16 records. Newer Python interpreters may need newer
dependency versions. The hosted macOS result applies to the exercised runner and
Python/dependency combination; it is not a guarantee for every macOS system.

See [limitations](limitations.md) for the approved first-import Python RNG effect
in the exercised scikit-learn/Rich versions. It does not change seeded plans.
