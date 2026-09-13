# 07 — Split auditing and design invariants

## 7.1 Validate structure first

Validate the split schema, unique fold keys, non-empty train and test sets, duplicate memberships, recognized observation IDs, objective compatibility and cohort digest. Structural errors must not be downgraded by a diagnostic option. A train/test observation intersection is always invalid for an ordinary out-of-sample evaluation, including diagnostic runs.

Within every outer fold, train and test must be disjoint and their union must equal the complete supplied cohort. Unknown or omitted IDs are actionable errors. Across complete CV test partitions within a repeat, each observation appears exactly once. Training observations may appear in several folds as usual. Imported multi-repeat plans can be audited repeat by repeat; v0.1.0 evaluation is restricted to exactly one repeat to keep aggregation unambiguous.

Imported one-off holdout plans are audited for within-fold separation/coverage but receive a clear `complete_cv=false` result, not a false failure simply because training observations are never tested. Their evaluation is unsupported in the first-release runner. Distinguish per-fold coverage from complete-CV test coverage.

## 7.2 Identity overlap

For each fold, independently intersect participant sets and protected-component sets across train/test. Under any supported unseen-person/domain objective, observed participant/component overlap is an error. Under audit_only, record the observed overlap as warning because no supported generalization objective has been selected; never declare it scientifically acceptable without that context.

Session-level checks use `(participant, session)` pairs. A session overlap from one participant is explanatory detail attached to participant overlap, not an independent count of unrelated failures. Distinct participants with the same session label do not overlap.

## 7.3 Domain constraints

For unseen_site, intersect site sets; for unseen_phase, intersect phase sets. Any shared held-out domain is an error. Under unseen_participant, shared sites are allowed and should be reported as the represented acquisition setting, not leakage. If a required domain value is missing, the domain check is unassessable and the evaluator is blocked.

An imported plan is assessed according to its objective, not according to a name such as `safe_split`. The file's objective must equal the run configuration. Renaming a plan cannot bypass constraints.

## 7.4 Class support

Record global class order and per-fold training/test support. A missing training class blocks classification for the full requested target space. A missing test class produces a warning and makes class-complete metrics undefined for that fold; do not silently remove the class or substitute a score of zero. Accuracy and supported per-class recalls can still be displayed.

A site containing only one class can be a legitimate observed dataset characteristic. If holding it out leaves training with all classes, the fold can run but some fold metrics are undefined. If a class exists only at the held-out site, that fold cannot train a classifier for that class; report design infeasibility.

## 7.5 Nested boundaries

Every inner training/validation ID must belong to its outer training set. Inner train and validation are disjoint, non-empty and jointly cover that outer training set. Outer test IDs must not appear in any inner split. Check participant and protected-component separation inside each inner fold. Inner validation coverage must be exactly once across the inner folds for tuning.

For site/phase-held-out outer evaluation, inner tuning protects participants/components; it does not automatically claim unseen-domain generalization because there may be too few training domains. Report this inner objective explicitly. Do not call a participant-grouped inner loop a site-held-out inner loop.

## 7.6 Audit outputs and severity

Return all independent meaningful split violations in a deterministic order. Structural unknown identities may block downstream checks for that fold; report not_assessable rather than performing a potentially wrong join. A report's execution completion is not the same as partition validity. `valid_for_objective` is a derived split summary that is false if required separation/prerequisite checks fail or cannot be assessed.

Do not publish a single trust score. Include the exact assumption checked, the count of affected units where safe, the fold scope and a corrective action. Default reports do not expose raw participant identifiers; a sensitive local export can expose them only on explicit request.
