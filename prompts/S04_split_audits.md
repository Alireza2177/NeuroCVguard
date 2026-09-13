# S04 — Split import and independent invariant auditing

**Requirement:** REQ-S04

**Entry gate:** S03 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Audit supplied partitions correctly at observation, participant, component, domain and nested levels.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/04_inputs_configuration.md`
- `spec/05_models_serialization.md`
- `spec/07_split_auditing.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S04
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S04 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S04.A — Load plans

Support canonical JSON and outer-only assignment TSV. Validate keys, objective, digest and identities. Bind null-digest imported plans after validation while retaining imported origin.

### S04.B — Implement invariants

Check within-fold membership, coverage, participant/components, objective-dependent domain separation and class support. Distinguish ordinary repeated training membership across folds from real train/test contamination.

### S04.C — Implement nested and coverage semantics

Verify inner containment/disjointness and outer-test exclusion. Audit one-fold holdouts and repeated imported CV correctly, while recording complete-CV status separately. Output all meaningful scoped failures without exposing IDs by default.

## Required deliverables

- load_split_plan and audit_splits
- Split/inner rule implementations
- Literal-set oracle tests
- Plan binding and imported TSV tests

## Acceptance gates

- Known leaky fixture gives participant-overlap errors
- Clean repeated-measures fixture has no participant-overlap error
- Shared sites are allowed for unseen_participant
- Outer test inside any inner fit is rejected

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S04-01 | Known participant overlap | Participant overlap detected even with no observation overlap. |
| AT-S04-02 | Clean repeated cohort | No subject/component overlap violations. |
| AT-S04-03 | Observation overlap | Always rejected including diagnostic mode. |
| AT-S04-04 | Across-fold train reuse | Repeated training membership across folds is not leakage. |
| AT-S04-05 | Allowed same sites | No site-separation violation. |
| AT-S04-06 | Forbidden same sites | Domain overlap error for the requested objective. |
| AT-S04-07 | Unknown member | Reject membership/identity mismatch; no positional lookup. |
| AT-S04-08 | Missing partition row | Per-fold coverage violation. |
| AT-S04-09 | Duplicate membership | Reject rather than collapse to a set silently. |
| AT-S04-10 | Missing training class | Evaluation blocked for that fold. |
| AT-S04-11 | Missing test class | Class-coverage warning; not an invented full-class score. |
| AT-S04-12 | Inner containment | Nested containment violation. |
| AT-S04-13 | Inner protected overlap | Protected-component violation. |
| AT-S04-14 | Holdout audit | Audit supported; complete_cv=false and evaluator not permitted. |
| AT-S04-15 | Repeated imported plans | Audit each repeat independently; baseline scope limit retained. |
| AT-S04-16 | Digest mismatch | Reject the plan/cohort binding. |
| AT-S04-17 | TSV import contract | Correct valid import; explicit invalid-role error. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S04.md` using the handoff template. Set S04 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

Do not generate, repair, resample or silently curate plans.
