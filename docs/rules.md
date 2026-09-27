# Rule catalog

Stable IDs from the rule register; checked against the register in documentation tests.
Severity applies when triggered; status and evidence kind remain distinct.
Read [warning actions](objectives.md) and [limitations](limitations.md).

| Rule | Finding | Severity / evidence | Meaning |
|---|---|---|---|
| `NCG-COHORT-001` | Repeated observations | info / observed | Inventory notice; repeated people are not by themselves a split violation. |
| `NCG-COHORT-002` | Within-participant target variation | warning / observed | Valid longitudinal possibility; baseline/stratified planning unsupported without explicit curation. |
| `NCG-COHORT-003` | Within-participant domain variation | info / observed | Describe crossing sites/phases; strict domain planning must assess feasibility. |
| `NCG-COHORT-004` | Exact feature equality across IDs | warning / heuristic | Observed equal vectors suggest review, not verified duplicate identity. |
| `NCG-COHORT-005` | Missing optional metadata | warning / unassessable | Requested checks without required metadata are not_assessable. |
| `NCG-COHORT-006` | Missing protected relationship data | error / unassessable | Strict splitting/evaluation blocked; unknown values not treated as independent. |
| `NCG-SPLIT-001` | Observation train/test overlap | error / observed | Never waived, including diagnostic evaluation. |
| `NCG-SPLIT-002` | Participant train/test overlap | error / observed | Violation for supported unseen-person objectives; warning under audit_only. |
| `NCG-SPLIT-003` | Protected-component overlap | error / observed | Crossing a declared dependence component invalidates the stated independent-unit design. |
| `NCG-SPLIT-004` | Requested held-out domain overlaps | error / observed | Only a separation violation for the corresponding unseen_site/unseen_phase objective. |
| `NCG-SPLIT-005` | Training class missing | error / observed | Cannot fit the requested full-class baseline for that fold. |
| `NCG-SPLIT-006` | Test class missing | warning / observed | Class-complete metrics undefined for this fold; retain other meaningful results. |
| `NCG-SPLIT-007` | Unknown or duplicate membership | error / observed | Structural membership diagnostic; reject invalid identity mapping. |
| `NCG-SPLIT-008` | Per-fold cohort coverage broken | error / observed | No silent exclusions or automatic row intersection. |
| `NCG-SPLIT-009` | Inner rows escape outer train | error / observed | Outer test or unknown IDs appear in an inner partition. |
| `NCG-SPLIT-010` | Inner partitions overlap or lack coverage | error / observed | Inner training/validation identities/components and completeness must hold. |
| `NCG-SPLIT-011` | Complete-CV coverage unavailable | warning / observed | A valid one-off holdout is auditable but outside complete-CV evaluation. |
| `NCG-PLAN-001` | Insufficient independent groups | error / observed | Requested fold count cannot be satisfied; do not downgrade automatically. |
| `NCG-PLAN-002` | Protected component crosses held-out domain | error / observed | Strict domain plan rejected without removing or relabeling observations. |
| `NCG-PLAN-003` | Stratification/class feasibility limitation | warning / observed | Document absent test-class feasibility; invalid actual training folds block plan. |
| `NCG-ASSOC-001` | Association review threshold crossed | warning / observed | Descriptive review signal, not proof of causal confounding or shortcut use. |
| `NCG-ASSOC-002` | Sparse contingency table | warning / observed | Small observed/expected counts make interpretation unstable; no p-value. |
| `NCG-ASSOC-003` | Association not assessable | warning / unassessable | Missing, constant, unstable or excessive-category input prevents specified statistic. |
| `NCG-PROV-001` | Upstream fitting history unknown | warning / unassessable | No automatic certification from a supplied feature matrix. |
| `NCG-PROV-002` | Declared global data-dependent fitting | warning / declared | User-declared information use outside training scope; not reconstructed history. |
| `NCG-PROV-003` | Declared fitting IDs violate scope | error / declared | Qualified declaration-based boundary finding; does not prove historical execution. |
| `NCG-PROV-004` | Observed internal fit scope violation | error / observed | Controlled runner defect; block successful evaluation and investigate. |
| `NCG-PROV-005` | Declared fixed non-learning transform | info / declared | No training-fit isolation requirement solely for a fixed row-local conversion. |
| `NCG-EVAL-001` | Fit failed or did not converge | error / observed | Incomplete run, no complete pooled score. |
| `NCG-EVAL-002` | Metric undefined | warning / observed | Null value plus specific reason; never substitute zero/NaN. |
| `NCG-EVAL-003` | Intentionally invalid diagnostic evaluation | warning / observed | Do not use as evidence for unseen-participant generalization. |
| `NCG-EVAL-004` | Training feature entirely missing | warning / observed | Document no training information and prescribed fold-local imputer handling. |
| `NCG-REPORT-001` | Sensitive operational output | info / observed | Identity-bearing split/private evaluation artifact; not a public report. |
