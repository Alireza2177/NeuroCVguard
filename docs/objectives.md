# Objectives and practical interpretation

| Objective | Required separation | Appropriate interpretation |
|---|---|---|
| `unseen_participant` | Participants and all declared transitive components | New people under represented acquisition conditions |
| `unseen_site` | Above plus site | People at a site absent from training |
| `unseen_phase` | Above plus phase | People from an acquisition phase absent from training |
| `audit_only` | Describes supplied memberships | No generated/evaluated predictive design |

A session is participant-local. Two visits from one person may be in the same
training partition; putting that person on both sides violates unseen-person
evaluation. A shared site is not automatically a violation for new people at known
sites. A participant or protected component spanning held-out domains makes strict
domain separation impossible without an explicit change to the input cohort or
objective. The tool refuses rather than dropping the difficult site.

| Finding | What to do next |
|---|---|
| Repeated observations | Inspect actual train/test participant membership. |
| Missing protected relationship | Obtain metadata; do not treat unknowns as independent. |
| Participant/component overlap | Correct supplied assignments or choose an explicitly different objective. |
| Domain crossing | Inspect identities and declare a feasible objective or separately documented curation. |
| Changing target | Keep the longitudinal audit; use a separately designed method outside this evaluator. |
| Acquisition–target association | Review class/domain counts and acquisition imbalance; this is not proof of causal confounding or shortcut use. |
| Unknown preprocessing | Obtain an explicit ledger or document what cannot be assessed. |
| Declared global PCA | Recompute data-dependent preprocessing within training subsets upstream; a later scaler cannot undo global PCA. |
| Missing test class | Retain the fold, accuracy and explicit null reasons; class-complete metrics may be undefined. |
| Suppressed metrics | Distinguish privacy suppression from mathematical undefinedness; detailed output needs an explicit local sensitive choice. |
| Failed fit | Retain the failed fold and incomplete status; no pooled complete score. |

See [evaluation](evaluation.md) for participant weighting, probability aggregation,
positive-class AUC and nested selection. A signed difference between designs is
descriptive: changing sites also changes the evaluation distribution.
