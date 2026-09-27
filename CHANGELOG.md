# Changelog

## Unreleased

- Revised documentation for clarity and corrected outdated prerelease statements.

## 0.1.0 — 2026-09-27

Initial research release, available on GitHub and PyPI under BSD-3-Clause.

### Features

- Strict local CSV, TSV and JSON input with explicit observation-key joins.
- Participant and transitive dependence checks, plus objective-specific site
  and phase separation checks.
- Auditing and generation of grouped cross-validation splits.
- Descriptive acquisition–target association and preprocessing provenance checks.
- Participant-level logistic regression evaluation with optional nested
  regularization selection.
- Descriptive comparison of supported evaluation designs.
- Offline HTML/JSON reports, privacy controls and five synthetic tutorials.

### Compatibility and limits

Private evaluation records can include paired `plan_digest` and `actual_plan`
fields. Comparison records can include typed design context. Current readers
accept older records without inventing missing values; older closed-schema
readers need updating. See the evaluation and comparison guides for details.

Remote and UNC paths are rejected before filesystem access, and target-label
aliases avoid collisions in reports. Source archives exclude internal fixtures
that are not package resources. Direct dependency lower bounds were tested.

The first import of scikit-learn/Rich can consume Python's global random state
in the tested environment. Seeded splits and NumPy state are unaffected; see
[limitations](docs/limitations.md). The maintainer walkthrough and independent-user
trial were deferred for this release and remain outstanding.

### Verification

The release passed 733 local tests and a six-job CI matrix covering Linux,
Windows, macOS and the direct dependency floor. Public GitHub/PyPI files match
the recorded checksums, and a fresh installation of the public wheel passed.
Earlier CI and publishing-tool failures, their fixes and the full command logs
are retained in the [release record](state/handoffs/S17.md).
