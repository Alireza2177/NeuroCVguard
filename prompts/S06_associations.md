# S06 — Descriptive acquisition–target association checks

**Requirement:** REQ-S06

**Entry gate:** S05 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Implement participant-level categorical diagnostics without overstating confounding or significance.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/06_identity_audits.md`
- `spec/09_association_diagnostics.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S06
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S06 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S06.A — Construct pairwise participant view

Require within-person stability for each covariate/target pair. Record complete/missing counts and skip unsupported unstable pairs without dropping people from the main cohort.

### S06.B — Compute known statistic

Build ordered contingency tables and use SciPy uncorrected Cramers V. Handle constant variables, observed zeros, sparse cells and category limits. Keep null reasons explicit.

### S06.C — Messages and reference tests

Register review-threshold and sparse-table warnings with descriptive language. Verify V=0/V=1 oracles, row/label invariance and repeated-observation invariance.

## Required deliverables

- Association diagnostics
- Per-pair denominator/support records
- Reference-statistic tests
- Conditional, noncausal recommendations

## Acceptance gates

- No p-value or causal-confounding verdict
- Repeating visits cannot multiply participant counts
- V=0 and V=1 fixtures agree with reference
- Constant/unstable pairs are unassessable, not zero

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S06-01 | Zero association | Cramers V equals zero within tight float tolerance. |
| AT-S06-02 | Perfect association | Cramers V equals one within tolerance. |
| AT-S06-03 | Constant variable | Null statistic with constant_variable reason. |
| AT-S06-04 | Repeat invariance | Participant table and V unchanged. |
| AT-S06-05 | Within-person covariate changes | Requested participant-level site pair is unassessable; no cherry-picked visit. |
| AT-S06-06 | Missing pairs | Complete and excluded participant counts documented; cohort unchanged. |
| AT-S06-07 | Sparse cells | Sparse warning without p-value or significance stars. |
| AT-S06-08 | High cardinality | Skip with too_many_categories rather than merge levels. |
| AT-S06-09 | Noncausal warning | Message requests review, not proof of model bias/leakage. |
| AT-S06-10 | Category-name invariance | V unchanged. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S06.md` using the handoff template. Set S06 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No naive permutations, mlconfound reimplementation, automatic ComBat or category merging.
