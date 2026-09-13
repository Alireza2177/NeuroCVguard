# 03 — Architecture, package boundaries and dependencies

## 3.1 Architectural shape

Use a conventional `src/` Python package. The core is a local library with a thin CLI and a static report renderer. Do not create a web backend, database, task queue or plugin registry.

```text
local CSV/TSV + JSON config + optional splits/features/declarations
                             |
                         strict I/O
                             |
                  typed cohort + split contracts
                     /        |         \
                 checks    split design  evaluator
                     \        |         /
                      structured results
                             |
                  privacy projection + rendering
                             |
              offline report + JSON + local split files
```

```text
src/neurocvguard/
    __init__.py                # intentionally small public exports
    __main__.py                # python -m neurocvguard
    config.py                  # loading and semantic validation
    models.py                  # public dataclasses and result records
    errors.py                  # documented domain exceptions
    io.py                      # strict local tables and keyed joins
    identity.py                # participants and protected components
    rules.py                   # rule metadata; not a plugin engine
    audit.py                   # orchestration, no fitting
    checks/
        cohort.py
        partitions.py
        associations.py
        provenance.py
    splitting.py               # standard sklearn adapters + invariant checks
    evaluation/
        baseline.py            # controlled estimator construction
        runner.py              # explicit fold execution
        metrics.py             # participant aggregation and valid metrics
        compare.py             # descriptive comparisons only
    reporting/
        json.py
        html.py
        privacy.py
        templates/report.html
        static/report.css
    datasets.py                # deterministic synthetic demo generation
    cli.py                     # argparse interface
    schemas/                   # packaged JSON schemas
    py.typed
```

This is a target layout, not an instruction to fill every file with a stub immediately. Create modules when their stage provides real behavior. Do not introduce base classes for speculative future formats. Shared utilities require at least two real callers or a demonstrated boundary.

## 3.2 Dependency direction

Models and configuration do not import the CLI or reporting. Checks are deterministic functions of validated inputs. Splitting returns a plan and independently audits it before returning success. Evaluation consumes validated plans and emits results; it does not repair plans. Reporting consumes structured results and must never recompute statistics differently from the API. The CLI delegates to the same public/library functions tested by Python examples.

Changes in a template cannot alter scientific results. Importing the package must not read a dataset, create a directory, start a worker, contact the internet or initialize an LLM client.

## 3.3 Technology choices

Use Python **3.11 or later**, with a mandatory initial test matrix of 3.11, 3.12 and 3.13. This is a compatibility target, not a claim that newer Python versions are unsupported or already tested. Add a newer interpreter only after its dependency installation and suite pass. Do not claim operating-system/interpreter combinations absent from recorded evidence.

Use `pathlib`, `argparse`, `logging`, `dataclasses`, `json`, `csv`, `hashlib` and `importlib.resources` from the standard library. Runtime scientific dependencies are NumPy, pandas, SciPy and scikit-learn. Use Jinja2 for escaped HTML and jsonschema for data contracts. Do not add PyTorch, TensorFlow, Nilearn, NiBabel, PyBIDS or fMRIPrep as runtime dependencies when no raw imaging operation requires them.

Use hatchling as the build backend, `pyproject.toml` as package metadata, pytest/pytest-cov and Hypothesis for tests, Ruff for formatting/linting, mypy for public/core typing, Sphinx with MyST and a standard theme for documentation, and build/twine for local distribution validation. Keep documentation and developer tools in optional extras. The conventional package/build choices are supported by PyPA guidance [R10, R11]; specific selections here are project decisions.

## 3.4 Dependency version policy

Stage S00 must test an actual compatible environment and record exact resolved versions. Do not invent future version numbers or freeze every dependency to whatever happened to be installed during code generation. Use lower bounds only after exercising the lowest supported environment. Major upper bounds may be used for demonstrated API compatibility boundaries; do not blindly add them to every dependency. Development lock/constraints files support reproducibility but must not force exact pins on downstream library users.

The ordinary install is `python -m pip install .`; developer install is `python -m pip install -e ".[dev,docs]"`. Both must be tested. A future `pip install neurocvguard` claim requires an actual public package release and ownership verification; before that, document source/wheel installation honestly.

## 3.5 Code quality

Public functions require type annotations and NumPy-style docstrings describing parameters, returns, exceptions, limitations and a minimal example. Use frozen dataclasses for lightweight result records where practical; do not pretend that a mutable pandas object is deeply immutable. Copy input data at public boundaries and test no-mutation guarantees.

Raise `ConfigurationError`, `InputValidationError`, `SplitValidationError`, `UnsupportedDesignError`, or `EvaluationError` with an actionable message. Do not catch all exceptions and return an empty report. Catch expected exceptions at the CLI boundary; unexpected failures retain a traceback under `--debug` without dumping patient rows.

A formatter determines routine style. Comments should explain intent, assumptions or non-obvious safeguards, not paraphrase the next line. README/API descriptions must reflect implemented behavior and actual supported versions.
