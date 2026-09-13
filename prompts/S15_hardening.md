# S15 — Adversarial, property, security and scientific review

**Requirement:** REQ-S15

**Entry gate:** S14 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Try to falsify the implementation against the specification rather than only confirming happy paths.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/04_inputs_configuration.md`
- `spec/05_models_serialization.md`
- `spec/06_identity_audits.md`
- `spec/07_split_auditing.md`
- `spec/08_split_generation.md`
- `spec/09_association_diagnostics.md`
- `spec/10_preprocessing_provenance.md`
- `spec/11_evaluation.md`
- `spec/12_design_comparison.md`
- `spec/13_reports_privacy.md`
- `spec/16_quality_tests.md`
- `spec/18_security_release.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S15
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S15 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S15.A — Adversarial coverage

Implement remaining acceptance cases and Hypothesis invariants; exercise malformed data, missing classes, transitive groups, hidden report data, low sample counts and platform paths.

### S15.B — Independent review and mutations

Use a separate review pass over actual code and source contracts. Verify critical tests catch the specified intentional faults; restore code and rerun. Record disagreements and human-review status honestly.

### S15.C — Performance/security evidence

Run resource/scaling benchmarks, verify no runtime networking or unsafe loaders, review dependencies/licenses/workflows and inspect privacy output. Fix defects without weakening gates.

## Required deliverables

- Completed case-to-test map
- Coverage and mutation evidence
- Measured benchmark/security record
- Scientific review findings and resolutions

## Acceptance gates

- Coverage thresholds and all mandatory cases pass
- No result-changing defect remains
- Actual resources are recorded without fabricated speed claims
- Review provenance distinguishes agent and human work

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S15-01 | Critical mutation detection | Targeted tests fail; restored code passes. |
| AT-S15-02 | Property stress | Specified invariants hold without flaky score assumptions. |
| AT-S15-03 | Coverage targets | Project/core thresholds met without unjustified exclusions. |
| AT-S15-04 | No hidden network | No outbound calls. |
| AT-S15-05 | Scaling benchmark | Measured cost documented and no accidental quadratic critical path. |
| AT-S15-06 | Large feature guard | Clear early refusal instead of uncontrolled allocation. |
| AT-S15-07 | Untrusted input instructions | Handled as inert data; never executed or followed. |
| AT-S15-08 | Independent review provenance | Actual findings and reviewer type recorded, not self-certified human review. |
| AT-S15-09 | No quality gate weakening | Every exception justified; no concealed failing requirement. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S15.md` using the handoff template. Set S15 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No scope expansion or hiding failing tests behind skips/tolerance changes.
