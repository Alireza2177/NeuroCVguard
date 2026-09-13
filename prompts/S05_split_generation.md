# S05 — Group-aware and held-out-domain plan generation

**Requirement:** REQ-S05

**Entry gate:** S04 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Generate deterministic plans using established splitters and independently verify their invariants.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/05_models_serialization.md`
- `spec/06_identity_audits.md`
- `spec/07_split_auditing.md`
- `spec/08_split_generation.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S05
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S05 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S05.A — Participant-grouped folds

Build one-row-per-person target table, map protected components, run StratifiedGroupKFold and expand memberships to observations. Use explicit seed and canonical order.

### S05.B — Domain folds

Implement LeaveOneGroupOut for requested site/phase objectives. Reject crossing participants/components, missing required domains and impossible class training. Do not prune data.

### S05.C — Validate and export

Run the independent split audit before returning success. Generate stable plan IDs/digests and sensitive local assignment exports. Record feasible warnings separately from invalid training conditions.

## Required deliverables

- make_splits
- Sensitive plan/assignment writers
- Deterministic group and domain tests
- Actionable infeasibility messages

## Acceptance gates

- All protected relationships stay intact
- No fallback to random splitting or seed search
- Generated plans pass independent audit
- Cross-site participants cause explicit domain-planning refusal

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S05-01 | Participant stratification unit | Stratification uses one record per participant, not visit multiplicity. |
| AT-S05-02 | Protected-group disjointness | Every protected component remains on one side of each fold. |
| AT-S05-03 | Too few groups | Explicit infeasibility; no fallback to random folds. |
| AT-S05-04 | Approximate stratification | Record actual support; do not promise exact balance. |
| AT-S05-05 | Crossing domain group | Generation rejected; cohort remains unchanged. |
| AT-S05-06 | Held-out phase | Each phase held out once with identity separation. |
| AT-S05-07 | No hidden repair | No row removal, merged label, changed seed or changed n_splits. |
| AT-S05-08 | Independent post-audit | make_splits refuses it after independent audit. |
| AT-S05-09 | Seed and order stability | Same expanded observation assignments. |
| AT-S05-10 | Global RNG preservation | State unchanged afterward. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S05.md` using the handoff template. Set S05 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No within-person forecasting, temporal split heuristics or automatic cohort selection.
