# Contributing

Bug reports, methodological questions and focused pull requests are welcome at
[NeuroCVguard on GitHub](https://github.com/Alireza2177/NeuroCVguard).
Use small synthetic examples; never attach patient data or private evaluation
records. Report security concerns privately as described in [SECURITY.md](https://github.com/Alireza2177/NeuroCVguard/blob/main/SECURITY.md).

## Development setup

Create a virtual environment and install the development dependencies from a
source checkout:

```text
python -m pip install -e ".[dev,docs]"
```

Run these checks in the same environment:

```text
python -m pytest -q --strict-markers --strict-config
python -m ruff check .
python -m ruff format --check .
python -m mypy src/neurocvguard
python -m sphinx -W --keep-going -b html docs docs/_build/html
```

For branch coverage, add `--cov=neurocvguard --cov-branch` to the pytest command.
To check specification documents, schemas and fixtures, run
`python tools/validate_foundation.py --mode artifacts`. This is separate from
application testing. The default `foundation` mode checks the original project
scaffold; use `artifacts` when working on the implemented package.

## Changes and review

Read the relevant specifications in `spec/` and schemas in `contracts/` before
changing scientific behavior. Repository working instructions are in `AGENTS.md`.
Keep changes focused and explain the problem, the new behavior and how you tested
it. Include the commands you ran and any checks you could not run.

Add a regression test for each bug fix. Prefer independent expected results,
checks of actual fit membership and synthetic fixtures. Preserve failed folds,
reasons for undefined metrics, explicit observation-key joins and privacy rules.
A failing test should lead to a fix or an explained design decision, not a weaker
assertion. Record schema decisions in an ADR and describe compatibility changes
in [CHANGELOG.md](https://github.com/Alireza2177/NeuroCVguard/blob/main/CHANGELOG.md).

Check dependency licenses and keep credentials, private inputs and identifying
outputs out of commits. Document substantial AI assistance and distinguish it
from review by a person. The [release guide](https://github.com/Alireza2177/NeuroCVguard/blob/main/docs/release.md) describes packaging,
verification and publication.
