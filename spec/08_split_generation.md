# 08 — Deterministic split generation

## 8.1 Use established algorithms

Delegate ordinary grouped stratification to `sklearn.model_selection.StratifiedGroupKFold` and domain holdout to `LeaveOneGroupOut`. The extra value is correct identity construction, target-unit handling, preflight feasibility checks, deterministic artifacts and independent validation. These are established group-aware splitters, not newly invented algorithms [R04, R06].

For subject_kfold, first construct one record per participant with its constant target and protected-component label. Run the splitter on that participant-level view with shuffle=True and the configured integer random seed. Expand participant assignments to all observations afterward. This prevents participants with many visits from receiving extra weight in the stratification objective. Families can contain participants with different classes; do not reduce an independence component to one guessed label.

## 8.2 Feasibility rules

Require at least n_splits independent components and at least two classes. Require constant, non-missing participant targets. Count independent components supporting each class. A class occurring in fewer than n_splits components means full test-class coverage is not feasible in every fold; report the limitation rather than pretending stratification will solve it. Fewer than two components supporting a class is a strong feasibility warning and may result in an invalid training fold.

Validate actual generated folds. If any training fold lacks a class or violates a required identity constraint, fail that requested plan with an explanation. Test folds missing classes may be retained with explicit warnings. Never silently reduce n_splits, drop participants, merge classes, change the seed, or fall back to random StratifiedKFold.

Stratification is an approximate allocation subject to indivisible groups; it is not a promise of identical class proportions. Class imbalance itself does not invalidate a partition.

## 8.3 Domain holdout

For leave_one_site_out, every participant and protected component must belong to exactly one site. For leave_one_phase_out, the same condition applies to phase. If a person or family spans domains, reject strict generation and explain the conflict. Do not prune their training observations, assign them to their most common site, or re-label the person to force a result. Those are different sampling designs requiring a future explicit decision.

Leave each represented domain out exactly once. The number of domains is the outer fold count; `n_splits` must be null. Require at least two domains. Validate class support and identity separation for every generated fold before exporting a usable plan.

## 8.4 Determinism and IDs

Canonicalize the participant table by stable participant order before invoking the splitter. Use only local random generators or explicit sklearn seeds; do not mutate NumPy's global RNG state. For fixed supported versions, input and seed, assignments must be identical. Record sklearn and NumPy versions because algorithm behavior may change across versions.

Assign fold IDs as zero-padded strings such as `fold-000`; repeat_id is `0` for generated plans. Build plan_id from a hash of the canonical plan contents excluding plan_id itself. Use the cohort digest binding defined in chapter 05. Record generator scheme and seed without claiming cryptographic reproducibility across every future dependency version.

## 8.5 No heuristic repair

A successful plan must have passed the same independent `audit_splits()` function used for user-supplied plans. Do not trust the generator's own bookkeeping alone. Save rejected-plan diagnostics separately, never as a normal plan with a reassuring name.

Recommendations may describe alternatives, such as collecting more sites or selecting an explicitly justified baseline visit. The software must not implement the alternative without a new user decision and a clearly changed cohort/configuration.
