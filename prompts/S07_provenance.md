# S07 — Declared preprocessing and runtime evidence model

**Requirement:** REQ-S07

**Entry gate:** S06 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Represent what can and cannot be known about preprocessing without claiming to reconstruct hidden pipeline history.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/05_models_serialization.md`
- `spec/07_split_auditing.md`
- `spec/10_preprocessing_provenance.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S07
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S07 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S07.A — Validate declaration ledger

Parse strict JSON events and fold references. Imported source is user_declaration; reject attempts to authenticate runtime claims through a string value.

### S07.B — Audit declared scopes

Compare declared fit IDs against relevant training sets. Distinguish global learning, unknown history, external transformations and fixed row-local operations.

### S07.C — Prepare observed event contract

Implement fit-boundary record types and validation helpers for the future runner. Add tests for truthful evidence labels and unassessable upstream operations; do not fabricate observed events before fits exist.

## Required deliverables

- Ledger parser and provenance checks
- Fit-event record contract
- Declared versus observed evidence tests
- Persistent upstream limitations

## Acceptance gates

- Unknown history cannot pass as verified
- Imported runtime labels remain declarations
- Fixed non-learning transforms are not blanket leakage
- Declared IDs outside train trigger appropriately qualified findings

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S07-01 | No ledger | Upstream history remains unassessable. |
| AT-S07-02 | Declared global fit | Qualified declared global-fit warning. |
| AT-S07-03 | Declared outside-training IDs | Declared boundary violation, not observed historical proof. |
| AT-S07-04 | Forged runtime label | Schema/loader rejects unsupported source. |
| AT-S07-05 | Fixed conversion | No blanket fitted-preprocessing leakage assertion. |
| AT-S07-06 | External learned transform | External provenance remains unassessable. |
| AT-S07-07 | No ghost fit events | No observed completed fit event is recorded. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S07.md` using the handoff template. Set S07 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No static Python/notebook code scanner, arbitrary execution or universal LeakagePipeline.
