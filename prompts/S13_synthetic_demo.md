# S13 — Synthetic generators and reproducible end-to-end demos

**Requirement:** REQ-S13

**Entry gate:** S12 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Deliver a first-run experience that works offline and illustrates the tool honestly.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/13_reports_privacy.md`
- `spec/14_interfaces.md`
- `spec/15_synthetic_examples.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S13
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S13 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S13.A — Generators

Implement documented local RNG scenarios clean, repeated and site_shift. Test shape/identity/determinism/mechanism parameters without asserting universal performance inflation.

### S13.B — Executable tutorials

Write the five required scripts and add demo CLI. Use only packaged synthetic data. Keep default demo non-diagnostic; opt-in scenarios disclose their intentional problems.

### S13.C — Capture actual outputs

Run every example in fresh temporary outputs, retain command/config/version evidence and produce a genuine report screenshot. Do not substitute conversational example numbers.

## Required deliverables

- Offline demo CLI
- Five runnable scripts
- Deterministic generators
- Actual demo reports and provenance

## Acceptance gates

- No downloads, account or real participant data
- Demo runs outside the source tree after wheel installation later
- Global RNG state remains unchanged
- Example claims match actual output

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S13-01 | Generator determinism | Exactly matching IDs, labels and numeric outputs in supported environment. |
| AT-S13-02 | Generator RNG isolation | Unchanged after demo generation. |
| AT-S13-03 | Mechanism isolation | Documented mechanism changes without hidden unrelated settings. |
| AT-S13-04 | Offline demo | Complete synthetic workflow and local report. |
| AT-S13-05 | Script execution | No missing hidden files or interactive state. |
| AT-S13-06 | Synthetic labeling | Fictitious data explicitly labeled; no real patient claims. |
| AT-S13-07 | Actual displayed results | Values match actual run or are explicitly hypothetical, never fabricated. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S13.md` using the handoff template. Set S13 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No real ADNI/AIBL distribution, biological realism claims or seed cherry-picking for a marketing metric.
