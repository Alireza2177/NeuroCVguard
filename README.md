# NeuroCVguard

Research-only Python software for checking whether supplied cohort identities,
partitions and evaluation procedures match an intended generalization claim.
It reads local CSV/TSV/JSON, checks participant/transitive dependence and requested
domain separation, describes acquisition–target association, generates checked
splits and runs a controlled participant-level logistic baseline with optional
nested C selection. Offline HTML/JSON reports retain incomplete coverage and
limitations. No account, GPU or runtime internet connection is needed.

It does not process MRI images, provide clinical advice, authenticate upstream
preprocessing, prove causal confounding or certify a study as leakage-free.
Repeated visits alone are not leakage; inspect actual membership and objective.
Unknown upstream preprocessing remains unassessable even with a correct Pipeline.

## Install and try

From an authorized local source checkout, create a dedicated Python environment.
Use `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on Linux/macOS
after `python -m venv .venv`. With that interpreter selected:

```text
python -m pip install -e ".[dev,docs]"
python -m neurocvguard demo --out local_outputs/demo
```

Open `local_outputs/demo/report.html`. Inputs are fully synthetic, not patient
data. Choose a new output path or explicitly use `--overwrite`. Read warnings
beside coverage: association suggests reviewing acquisition imbalance, while
unknown preprocessing asks for evidence rather than a passing verdict.

**Private plans/evaluations are separate from projected reports.** Default
projection is not guaranteed anonymity; inspect artifacts before sharing.
Version: 0.1.0. See the [release procedure and evidence](docs/release.md) for
publication status and the actual verified installation/platform results.

## Documentation and development

- [Installation and troubleshooting](docs/installation.md)
- [Executable quickstart](docs/quickstart.md) and [synthetic tutorials](docs/synthetic_examples.md)
- [Inputs](docs/input_tables.md), [configuration](docs/configuration.md),
  [CLI](docs/cli.md) and [Python API](docs/api.rst)
- [Objectives/warning actions](docs/objectives.md), [evaluation](docs/evaluation.md),
  [report privacy](docs/reporting.md) and [limitations](docs/limitations.md)
- [Contributing/testing](CONTRIBUTING.md), [changelog](CHANGELOG.md),
  [security](SECURITY.md) and [release procedure](docs/release.md)

Build the full local site with
`python -m sphinx -W --keep-going -b html docs docs/_build/html` and open
`docs/_build/html/index.html`. Run
`python -m pytest -q --strict-markers --strict-config` for the test suite.
Actual stage evidence and unrun checks are recorded under `state/handoffs/`.
Local Windows and Linux WSL2 checks and the Python 3.11 direct-dependency floor
have been exercised; see [installation evidence](docs/installation.md).
macOS and hosted CI remain unverified until their recorded runs pass.

## License, support and citation

Copyright 2026 Alireza Emad. Released under the [BSD-3-Clause license](LICENSE).
Maintainer: Alireza Emad. For private security reports, use the approved contact in
[SECURITY.md](SECURITY.md); share only synthetic reproductions. No response-time
or long-term support commitment is claimed.
Citation metadata will be added only after verified authorship and release details;
no DOI or citation badge exists. [AI assistance](AI_ASSISTANCE.md) is recorded
honestly. Human walkthrough, external-user testing and acceptance remain pending.
