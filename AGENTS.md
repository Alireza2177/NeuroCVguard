# NeuroCVguard — repository instructions

Build the local, research-only Python tool defined in `spec/`. Product name: NeuroCVguard; distribution/import/CLI: neurocvguard. This foundation is not an implemented application.

## Read before editing

Read `START_HERE.md`, `state/PROJECT_STATUS.json`, the selected `prompts/Sxx_*.md`, its listed spec chapters, relevant acceptance cases in `qa/acceptance_cases.json`, and the last accepted handoff. Open the files; do not assume a mentioned file was read. Report the actual instruction sources loaded.

Implement only the selected stage. Treat `spec/` and `contracts/` as the normative source; the master document is a generated reading copy. If contracts conflict, stop the affected work, record a concrete counterexample and an ADR, and request a decision. Do not silently weaken requirements.

## Non-negotiable scientific rules

- Repeated observations alone are not leakage. Check actual train/test membership and the stated objective.
- Protect participant identity and transitive declared dependence components. Session IDs are participant-local; never split subjects by `(subject, session)` tuples.
- Shared sites are not universally leakage. Domain separation is objective-dependent.
- Acquisition/target association is descriptive, not proof of causality or model shortcut use.
- Unknown upstream preprocessing remains unassessable. A Pipeline cannot repair earlier global fitting.
- Use ordinary sklearn splitters and Pipeline, not a universal “LeakagePipeline.”
- Join by explicit observation keys, never row order. No silent dropping, relabeling, seed hunting or splitter fallback.
- Constant participant target is required for the v0.1 classification evaluator. Unsupported longitudinal/temporal/regression designs are not guessed.
- Every fit is restricted to the correct current training subset. Inner selection cannot see outer-test data.
- Undefined metrics are null plus reasons. Failed folds cannot disappear from aggregate results.
- A score difference between designs is descriptive, not an automatic causal estimate of leakage.
- No trust score, clinical certificate, global leakage-free verdict or unsupported novelty claim.

## Engineering and privacy

Use the src layout, typed small functions, pytest, standard sklearn/SciPy components and strict local JSON/CSV/TSV. No raw image processing, GPU requirement, cloud/API dependency, dynamic user code, unsafe deserialization, automatic dataset downloads or telemetry.

Preserve unrelated files. Do not clobber outputs without explicit permission. No destructive git reset/clean. Keep secrets and real participant data out of prompts, public history, tests and logs. Reports are escaped and privacy-projected; identity-bearing split plans and private evaluation records are separately marked sensitive. No public push, upload, DOI registration or visibility change without human authorization.

## Quality and handoff

Implement specified tests alongside behavior. Run relevant checks and regressions. Never invent test counts, outputs, benchmark values, CI results, users, contributors, dates, citations or approvals. Do not delete failing tests, weaken assertions or add unexplained skips to make a run green.

Record exact commands, exit codes, environment and results in `state/handoffs/Sxx.md`. Mark unrun checks NOT RUN. Codex may set READY_FOR_REVIEW; ACCEPTED requires explicit human approval. A separate AI review is not human review. Stop at the stage boundary unless sequential work was explicitly authorized.

Use clear conventional code/docs rather than AI-style marketing or boilerplate. Keep an accurate assistance/review record; never disguise AI involvement through fabricated history. Maintainer authorship and licensing fields must be real before public release.

## Commands as they become available

`python -m pytest -q --strict-markers --strict-config`
`python -m ruff check .`
`python -m ruff format --check .`
`python -m mypy src/neurocvguard`
`python -m sphinx -W --keep-going -b html docs docs/_build/html`
`python -m build`

Do not claim a command passed before its tooling/files exist. The standalone foundation validator checks specification consistency only, not application functionality.
