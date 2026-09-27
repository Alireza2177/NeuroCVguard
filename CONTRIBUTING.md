# Contributing

This is local research software under development. There is no verified public
repository/support URL yet. Discuss changes through the existing project owner
channel; use synthetic reproductions only. Read AGENTS.md and the relevant spec
and contracts before changing scientific behavior.

Create a dedicated environment and install `python -m pip install -e ".[dev,docs]"`.
Run `python -m pytest -q --strict-markers --strict-config`,
`python -m ruff check .`, `python -m ruff format --check .`,
`python -m mypy src/neurocvguard`, and
`python -m sphinx -W --keep-going -b html docs docs/_build/html`.
Coverage uses `python -m pytest -q --strict-markers --strict-config --cov=neurocvguard --cov-branch`.
Use the same environment for every command. Platform evidence must describe the
actual platform; the planned matrix is not a claim of support.

For document/schema/fixture consistency, run
`python tools/validate_foundation.py --mode artifacts`. This does not certify
application behavior or human acceptance. The default `foundation` mode retains
the original untouched-foundation checks and intentionally rejects progressed
stage records. Both modes leave files untouched unless `--output PATH` names a
new evidence file; existing output files are refused.

Tests should use independent set/probability oracles, fit spies and synthetic
fixtures. Keep failed folds, null reasons, explicit joins and privacy projections.
Do not remove failing tests, inflate tolerances or silently relax contracts.
Add a regression test for each defect. Document intentional behavioral changes
and compatibility in CHANGELOG.md; schema conflicts require a concrete ADR.

Use small focused changes with the problem, resulting behavior and actual commands
in the PR template. Do not include private inputs, raw identity-bearing outputs,
credentials or copied code without reviewed license compatibility. Record AI
assistance and actual reviewer type honestly. Human acceptance and publication
are separate decisions. See docs/release.md for the release checklist.
