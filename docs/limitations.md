# Limitations and privacy boundaries

NeuroCVguard checks supplied tabular identities, declared relationships and
partitions. Unknown upstream preprocessing remains **unassessable**. A Pipeline
only controls the transformations fitted inside it. An imported declaration,
digest or fit record cannot authenticate historical execution.

The evaluator supports binary/multiclass classification with a constant target per
participant, one repeat, at least two outer folds and exactly-once test coverage.
It does not support regression, forecasting, changing-target longitudinal
evaluation, survival analysis, repeated-CV pooling or holdout-only scoring.
It processes no MRI images and provides no clinical advice, global leakage-free
verdict, trust score, causal bias estimate or guarantee about target proxies.

Participant aliases supplied under different IDs cannot be resolved automatically.
Feature equality is a review heuristic, not proof of shared identity. Audits cannot
reconstruct test-set adaptation. Freeze plans and record amendments independently.

Default reports omit raw identities, paths, hashes and open evidence and suppress
small cells. Counts, structural relationships and projected class labels can still
reveal information; this is **not formal anonymization**. Private plans/evaluations
and explicit sensitive reports require authorized local handling. Read
[reporting](reporting.md) before sharing any artifact. Debug output is sanitized,
but review it yourself before sharing.

Version 0.1.0 has been released, with installation and CI results documented in
[release verification](release.md). It has not undergone an independent-user trial
or independent human scientific validation. The planned report screenshot review
was not completed because capture was blocked by the browser security policy.
Saved reports and numerical consistency checks are available, but they do not
replace a visual review.

In the exercised scikit-learn 1.9.1 / Rich 15.0.0 environment, the first lazy
dependency import consumes Python's global RNG for progress-bar style identifiers.
NumPy state is unchanged, seeded plans are identical, and subsequent scientific
calls preserve both RNG states. This first-import behavior is documented in
{download}`ADR-S15-001 <../state/decisions/ADR-S15-001-cold-dependency-rng.md>`.
No process-global RNG restoration is attempted because it could overwrite other
threads' draws. Algorithmic determinism and training-boundary tests remain enforced.
