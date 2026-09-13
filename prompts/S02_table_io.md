# S02 — Strict tables, identities and keyed feature joins

**Requirement:** REQ-S02

**Entry gate:** S01 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Read valid local tables without losing identities or silently changing the cohort.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/03_architecture.md`
- `spec/04_inputs_configuration.md`
- `spec/05_models_serialization.md`
- `spec/18_security_release.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S02
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S02 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S02.A — Parse metadata conservatively

Read CSV/TSV with explicit delimiter and UTF-8/BOM support. Detect duplicate headers and malformed rows before pandas coercion. Preserve zero-prefixed and Unicode IDs; enforce whitespace/control-character rules.

### S02.B — Implement role and feature checks

Validate role mappings, missing tokens and collisions. Align feature tables by one-to-one key matching. Reject extra/missing IDs and prohibited predictor roles. Convert only selected numeric features; reject infinity and unsupported data types.

### S02.C — Resource and mutation tests

Apply file and dense-size guards before avoidable allocations. Test paths with spaces/Unicode, shuffled input rows, unsupported formats, safe errors and DataFrame immutability. Implement canonical cohort/feature digest functions.

## Required deliverables

- load_cohort and supporting I/O
- Strict feature joins
- Resource guards and digests
- Detailed input contract tests

## Acceptance gates

- 001 and 1 remain distinct
- Reordering feature rows does not change aligned values
- Missing/extra join keys never disappear silently
- Row reordering preserves cohort digest; mapped-value changes alter it

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S02-01 | Leading zeros | Two distinct participants/observation keys are preserved. |
| AT-S02-02 | Duplicate headers | InputValidationError before dataframe auto-renaming. |
| AT-S02-03 | UTF-8 BOM | Correct header recognition and exact legitimate IDs. |
| AT-S02-04 | Whitespace identity | Reject with sanitized repair message; do not trim silently. |
| AT-S02-05 | Missing critical ID | Fatal validation error; no assigned synthetic identity. |
| AT-S02-06 | NA vocabulary | NA stays a string; n/a is recognized missing. |
| AT-S02-07 | Duplicate observation ID | Input rejected; no drop_duplicates fallback. |
| AT-S02-08 | Shuffled feature rows | Features align exactly by observation ID. |
| AT-S02-09 | Missing feature key | Join fails with missing count, not silent row intersection. |
| AT-S02-10 | Extra feature key | Join fails explicitly. |
| AT-S02-11 | Prohibited predictors | Configuration/input validation refuses it. |
| AT-S02-12 | Numeric coercion | Input fails; recognized missing numeric cells remain missing. |
| AT-S02-13 | DataFrame identity type | Refuse lossy implicit conversion and explain string requirement. |
| AT-S02-14 | No input mutation | Original metadata/features remain unchanged. |
| AT-S02-15 | Unsupported sources | Reject unsupported local format without network/deserialization. |
| AT-S02-16 | Allocation guard | Refuse before constructing avoidable dense arrays. |
| AT-S02-17 | Digest invariance | Reorder retains digest; mapped change changes digest. |
| AT-S02-18 | Paths with spaces | No shell quoting or hard-coded slash assumption. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S02.md` using the handoff template. Set S02 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No automatic BIDS scan discovery, raw image reading, patient downloads or cleaning by silent row deletion.
