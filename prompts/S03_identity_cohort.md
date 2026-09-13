# S03 — Participant, dependency and cohort checks

**Requirement:** REQ-S03

**Entry gate:** S02 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Build the identity model and accurate cohort inventory with evidence-aware findings.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/04_inputs_configuration.md`
- `spec/06_identity_audits.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S03
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S03 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S03.A — Implement participant inventory

Count observations and people separately, inspect target stability and participant-local sessions, and report missing mapped fields. Repeated visits are an informational design cue, not confirmed leakage.

### S03.B — Build protected components

Implement union–find with field namespaces and transitive participant links. Report incomplete relationships without grouping missing values together. Preserve cross-site participant identity.

### S03.C — Add equality and variation checks

Add exact selected-feature equality using hashing plus confirmation, skip all-missing vectors and keep heuristic interpretation. Describe site/phase changes within participants. Register stable cohort rule IDs and messages.

## Required deliverables

- Identity components
- Cohort audit checks
- Initial rule registry
- Unit/property tests for grouping and no false identity matches

## Acceptance gates

- Shared ses-01 across people creates no false linkage
- Transitive family/duplicate links form one component
- Feature equality does not merge participants
- Repeated observations alone do not create an observed-leakage conclusion

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S03-01 | People versus observations | Inventory gives 18 people and 36 observations. |
| AT-S03-02 | Repeated participants are not leakage | Informational repeat notice; no observed split violation. |
| AT-S03-03 | Global session labels | Distinct people are not linked by session text. |
| AT-S03-04 | Changing diagnosis | Describe target variation; block constant-target baseline eligibility without relabeling. |
| AT-S03-05 | Transitive dependency | A/B/C form one protected component. |
| AT-S03-06 | Dependency namespaces | No cross-field equality link unless an actual participant bridges them. |
| AT-S03-07 | Missing protected field | Strict planning/evaluation blocked; missing values not grouped together. |
| AT-S03-08 | Cross-site participant | One identity retained; descriptive crossing notice. |
| AT-S03-09 | Exact feature equality | Heuristic review finding; no identity merge/drop. |
| AT-S03-10 | All-missing vectors | Skip duplicate-equality inference for those vectors and record reason. |
| AT-S03-11 | Component ordering | Same memberships and deterministic component identifiers. |
| AT-S03-12 | Hash collision confirmation | Exact comparison prevents a false equality finding. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S03.md` using the handoff template. Set S03 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No split generation, causal inference or automatic participant deduplication.
