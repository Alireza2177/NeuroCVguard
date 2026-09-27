# NeuroCVguard

NeuroCVguard helps researchers check training and test splits in neuroimaging
machine learning studies. It audits participant overlap and declared relationships,
checks site separation against the study objective, and reports what can and
cannot be assessed from the supplied data.

The package works with local CSV, TSV and JSON files. It can generate grouped
splits, run a participant-level logistic regression baseline with optional nested
regularization selection, and produce offline HTML and JSON reports. No account,
GPU or internet connection is needed after installation.

NeuroCVguard is research software. It does not process MRI images or certify a
study as leakage-free. Repeated visits alone are not leakage: the relevant question
is whether related observations cross the training and test boundary. Unknown
upstream preprocessing remains unassessable, even when later steps use a Pipeline.

## Install and try

Use Python 3.11 or newer in a virtual environment:

```text
python -m venv .venv
```

Activate the environment, or use `.venv/Scripts/python.exe` on Windows and
`.venv/bin/python` on Linux/macOS in place of `python` below:

```text
python -m pip install neurocvguard==0.1.0
python -m neurocvguard demo --out local_outputs/demo
```

Open `local_outputs/demo/report.html` to explore a fully synthetic example.
Choose a new output directory for each run, or use `--overwrite` to replace a
previous run's files.

Read findings alongside their coverage and limitations. For example, a
scanner–target association is a reason to inspect acquisition imbalance; it does
not prove that a model uses a shortcut. Missing preprocessing history requires
further evidence, rather than a passing result.

Split plans and private evaluation records contain observation identifiers.
Reports omit selected identifiers and suppress small cells, but may still disclose
sensitive information. Review all files before sharing them.

## Documentation

- [Installation](docs/installation.md) and [quickstart](docs/quickstart.md)
- [Synthetic examples](docs/synthetic_examples.md)
- [Input tables](docs/input_tables.md), [configuration](docs/configuration.md),
  [CLI](docs/cli.md) and [Python API](docs/api.rst)
- [Evaluation objectives](docs/objectives.md), [model evaluation](docs/evaluation.md),
  [report privacy](docs/reporting.md) and [limitations](docs/limitations.md)
- [Contributing](CONTRIBUTING.md), [changelog](CHANGELOG.md) and
  [release verification](docs/release.md)

To build the documentation from a source checkout:

```text
python -m pip install -e ".[dev,docs]"
python -m sphinx -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`. Development and test commands are in
[CONTRIBUTING.md](CONTRIBUTING.md).

## License, citation and support

Maintained by Alireza Emad. Copyright 2026 Alireza Emad.
Licensed under [BSD-3-Clause](LICENSE).

Use [CITATION.cff](CITATION.cff) to cite version 0.1.0. The release is available on
[PyPI](https://pypi.org/project/neurocvguard/0.1.0/) and
[GitHub](https://github.com/Alireza2177/NeuroCVguard/releases/tag/v0.1.0).

Report bugs through [GitHub Issues](https://github.com/Alireza2177/NeuroCVguard/issues)
using a small synthetic example. Send security concerns through the private
contact in [SECURITY.md](SECURITY.md). See the [development record](AI_ASSISTANCE.md)
for assistance and review details.
