# S12 — Design comparison and gated diagnostic examples

**Requirement:** REQ-S12

**Entry gate:** S11 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Compare design outputs without confusing distribution changes with a measured amount of leakage.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/07_split_auditing.md`
- `spec/11_evaluation.md`
- `spec/12_design_comparison.md`
- `spec/14_interfaces.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S12
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S12 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S12.A — Build comparison records

Load private evaluation records; check comparable cohort/features/classes/units. Preserve signed deltas and mismatch reasons; never select a winning scientific design.

### S12.B — Implement narrow diagnostic mode

Allow explicit row-random participant-overlap diagnostics only under the chapter 12 restrictions. Keep all structural guards and unmistakable invalid-for-objective labeling.

### S12.C — Expose and test

Add compare CLI and comparison report. Test negative differences, incomparable runs, incomplete results, suppression projection and unauthorized diagnostic waivers.

## Required deliverables

- compare_designs and compare CLI
- Diagnostic-only evaluation path
- Comparison/null/mismatch tests
- Explanatory report language

## Acceptance gates

- No delta when cohorts/features/units mismatch
- Negative differences are retained
- Diagnostic option cannot waive observation overlap or domain/family constraints
- Every diagnostic report states invalidity for unseen-person evidence

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S12-01 | Signed delta | Negative delta preserved. |
| AT-S12-02 | Mismatched cohort | Delta null and mismatch reason. |
| AT-S12-03 | Mismatched feature/unit | No misleading paired delta. |
| AT-S12-04 | Diagnostic default off | Evaluation blocked. |
| AT-S12-05 | Narrow diagnostic permit | Runs labeled diagnostic_only and invalid for stated generalization. |
| AT-S12-06 | No observation waiver | Still blocked. |
| AT-S12-07 | No family/domain waiver | Still blocked. |
| AT-S12-08 | Public/private compare boundary | Actionable request for operational evaluation record; no guessed digests. |
| AT-S12-09 | No causal conclusion | Interpretation distinguishes changed distribution from causal leakage quantity. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S12.md` using the handoff template. Set S12 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No causal optimism estimator, significance tests or best-design leaderboard.
