# Stable rule catalog

Severity here is the triggered default. A pass uses the same rule ID with a scoped message; missing inputs must not masquerade as a pass. Where objective-specific severity differs, the Meaning column controls. The catalog is not a composite trust score. Structural input errors may expose the diagnostic ID through a documented exception instead of fabricating a completed report.

| Rule | Name | Severity | Evidence | Meaning | Stage |
|---|---|---|---|---|---|
| NCG-COHORT-001 | Repeated observations | info | observed | Inventory notice; repeated people are not by themselves a split violation. | S03 |
| NCG-COHORT-002 | Within-participant target variation | warning | observed | Valid longitudinal possibility; baseline/stratified planning unsupported without explicit curation. | S03 |
| NCG-COHORT-003 | Within-participant domain variation | info | observed | Describe crossing sites/phases; strict domain planning must assess feasibility. | S03 |
| NCG-COHORT-004 | Exact feature equality across IDs | warning | heuristic | Observed equal vectors suggest review, not verified duplicate identity. | S03 |
| NCG-COHORT-005 | Missing optional metadata | warning | unassessable | Requested checks without required metadata are not_assessable. | S03 |
| NCG-COHORT-006 | Missing protected relationship data | error | unassessable | Strict splitting/evaluation blocked; unknown values not treated as independent. | S03 |
| NCG-SPLIT-001 | Observation train/test overlap | error | observed | Never waived, including diagnostic evaluation. | S04 |
| NCG-SPLIT-002 | Participant train/test overlap | error | observed | Violation for supported unseen-person objectives; warning under audit_only. | S04 |
| NCG-SPLIT-003 | Protected-component overlap | error | observed | Crossing a declared dependence component invalidates the stated independent-unit design. | S04 |
| NCG-SPLIT-004 | Requested held-out domain overlaps | error | observed | Only a separation violation for the corresponding unseen_site/unseen_phase objective. | S04 |
| NCG-SPLIT-005 | Training class missing | error | observed | Cannot fit the requested full-class baseline for that fold. | S04 |
| NCG-SPLIT-006 | Test class missing | warning | observed | Class-complete metrics undefined for this fold; retain other meaningful results. | S04 |
| NCG-SPLIT-007 | Unknown or duplicate membership | error | observed | Structural membership diagnostic; reject invalid identity mapping. | S04 |
| NCG-SPLIT-008 | Per-fold cohort coverage broken | error | observed | No silent exclusions or automatic row intersection. | S04 |
| NCG-SPLIT-009 | Inner rows escape outer train | error | observed | Outer test or unknown IDs appear in an inner partition. | S04 |
| NCG-SPLIT-010 | Inner partitions overlap or lack coverage | error | observed | Inner training/validation identities/components and completeness must hold. | S04 |
| NCG-SPLIT-011 | Complete-CV coverage unavailable | warning | observed | A valid one-off holdout is auditable but outside complete-CV evaluation. | S04 |
| NCG-PLAN-001 | Insufficient independent groups | error | observed | Requested fold count cannot be satisfied; do not downgrade automatically. | S05 |
| NCG-PLAN-002 | Protected component crosses held-out domain | error | observed | Strict domain plan rejected without removing or relabeling observations. | S05 |
| NCG-PLAN-003 | Stratification/class feasibility limitation | warning | observed | Document absent test-class feasibility; invalid actual training folds block plan. | S05 |
| NCG-ASSOC-001 | Association review threshold crossed | warning | observed | Descriptive review signal, not proof of causal confounding or shortcut use. | S06 |
| NCG-ASSOC-002 | Sparse contingency table | warning | observed | Small observed/expected counts make interpretation unstable; no p-value. | S06 |
| NCG-ASSOC-003 | Association not assessable | warning | unassessable | Missing, constant, unstable or excessive-category input prevents specified statistic. | S06 |
| NCG-PROV-001 | Upstream fitting history unknown | warning | unassessable | No automatic certification from a supplied feature matrix. | S07 |
| NCG-PROV-002 | Declared global data-dependent fitting | warning | declared | User-declared information use outside training scope; not reconstructed history. | S07 |
| NCG-PROV-003 | Declared fitting IDs violate scope | error | declared | Qualified declaration-based boundary finding; does not prove historical execution. | S07 |
| NCG-PROV-004 | Observed internal fit scope violation | error | observed | Controlled runner defect; block successful evaluation and investigate. | S10 |
| NCG-PROV-005 | Declared fixed non-learning transform | info | declared | No training-fit isolation requirement solely for a fixed row-local conversion. | S07 |
| NCG-EVAL-001 | Fit failed or did not converge | error | observed | Incomplete run, no complete pooled score. | S10 |
| NCG-EVAL-002 | Metric undefined | warning | observed | Null value plus specific reason; never substitute zero/NaN. | S10 |
| NCG-EVAL-003 | Intentionally invalid diagnostic evaluation | warning | observed | Do not use as evidence for unseen-participant generalization. | S12 |
| NCG-EVAL-004 | Training feature entirely missing | warning | observed | Document no training information and prescribed fold-local imputer handling. | S10 |
| NCG-REPORT-001 | Sensitive operational output | info | observed | Identity-bearing split/private evaluation artifact; not a public report. | S08 |
