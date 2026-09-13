# 16 — Test strategy, acceptance oracles and quality gates

## 16.1 What evidence counts

A passing test suite is necessary but not sufficient for scientific credibility. The suite must test negative cases, data-boundary violations, undefined metrics and honest reporting, not just successful execution. The requirement register and acceptance-case register in qa/ are normative. Tests added by Codex should cite case IDs in their names or docstrings and maintain a machine-readable mapping to those IDs.

The foundation's own validator tests document/schema/fixture consistency only. It does not validate the future package. Keep these two kinds of evidence separate.

## 16.2 Test layers

**Unit:** exact set operations, identity components, strict configuration, keyed joins, statistic definitions, metric null rules, schema serialization and privacy projection.
**Property:** row-permutation invariance; ID-renaming invariance; protected-group disjointness for arbitrary valid generated examples; no global-RNG mutation; duplicate-count invariance of participant association; serialization round trips; no input mutation.
**Integration:** API-to-CLI equivalence, report generation, complete baseline, tuning boundaries, graceful infeasibility, commands in directories containing spaces/Unicode, and offline execution.
**Packaging:** source install, editable install, wheel/sdist build, installation of the wheel in a clean directory, included schemas/templates/assets and working console entry point.
**Documentation:** executable quickstart scripts, valid internal links, strict Sphinx build, API completeness and screenshots from actual synthetic output.

Use pytest's ordinary fixtures/temporary directories and supported collection conventions [R12]. Hypothesis is for invariants, not random re-running until a desired score occurs [R13].

## 16.3 Independent oracles

Set-overlap expected results must come from literal fixture memberships. Cramer's V examples include hand-checkable V=0 and V=1 tables. Metric oracles use fixed probability arrays and independently computed confusion counts plus explicit reference-library calls. Nested-fit tests use spies that record IDs observed during fit. Do not assert against a second wrapper around the same buggy production helper.

At least one test must fail for each of these intentional defects: joining by row order; grouping by participant/session tuple instead of participant; treating a global session label as identity; using tuples instead of transitive components; globally fitting the scaler; leaking outer-test rows into inner tuning; silently dropping a difficult site; reporting undefined AUC as zero; hiding a failed fold in an average; stripping IDs in one output but leaking them in embedded JSON.

Implement a focused mutation check or explicitly run a temporary controlled patch to establish that critical tests detect these faults. Restore the production code afterward and retain the review evidence. Do not add a complex mutation-testing service just for a badge.

## 16.4 Coverage thresholds

Release acceptance targets: at least 90% line coverage and 85% branch coverage for the package, and at least 95% line coverage for identity/partition/metric modules. These are engineering thresholds selected for this project, not proof of scientific correctness. All public error paths and mandatory acceptance cases must still be exercised. Do not pad coverage by testing trivial generated accessors or exclude difficult modules without an approved reason.

No unexplained xfail, skip, broad warning suppression or platform disablement is allowed in the release evidence. Legitimate platform-specific behavior needs an explicit reason and an equivalent tested contract where possible.

## 16.5 Standard quality commands

By the relevant stages, these commands must be real and runnable:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src/neurocvguard
python -m pytest -q --strict-markers --strict-config --cov=neurocvguard --cov-branch
python -m sphinx -W --keep-going -b html docs docs/_build/html
python -m build
python -m twine check dist/*
```

The shell wildcard in the final command must have an equivalent Python/path-expansion implementation for shells that do not expand it. Do not insist on Bash for Windows acceptance. Tool-specific configuration belongs in pyproject.toml or standard tool files; do not create a giant custom task framework.

## 16.6 CI matrix

Run the full primary suite on Linux with Python 3.11/3.12/3.13. Run at least core, CLI, report and wheel-install tests on Windows and macOS with Python 3.12. Pin actions to audited full commit SHAs when creating workflows, record actual versions, and set minimal permissions. A dependency-compatibility job exercises the lowest declared dependency environment. An optional newest-supported environment catches upcoming incompatibilities but must not be presented as verified support until it passes.

PR jobs never receive publication secrets and must not use pull_request_target to execute untrusted code with elevated privileges. Ordinary tests require no network. Dependency installation may use approved registries during setup; runtime internet access is not part of the product.

## 16.7 Resource/performance acceptance

Benchmark metadata audit/splitting on a reproducible synthetic 10,000-observation cohort and a larger 100,000-row inventory case. Benchmark a modest feature baseline separately. Record hardware, versions, elapsed time, peak memory, dimensions and algorithmic scaling; do not invent a universal time target before measurement. Detect accidental quadratic duplicate/group checks with scaling tests. Enforce configured resource limits and confirm that oversized jobs fail before large allocations.

Use short deterministic unit cases in every PR and mark larger benchmarks separately. Performance optimization must not weaken scientific invariants or silently truncate input.

## 16.8 Release-defect policy

A known result-changing bug blocks release. A noncritical cosmetic issue may be documented with an issue and user-visible limitation. A discovered published metric/split defect requires a transparent changelog, corrected version and, where needed, a warning about affected earlier versions. Never silently replace benchmark artifacts while leaving the reported version unchanged.
