# S08 — Shared JSON/HTML reporting and privacy boundaries

**Requirement:** REQ-S08

**Entry gate:** S07 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Make findings understandable while keeping sensitive operational artifacts distinct from public reports.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/05_models_serialization.md`
- `spec/13_reports_privacy.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S08
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S08 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S08.A — Implement report projection

Centralize raw-ID/path/domain aliasing and small-cell suppression. Remove suppressed table totals, percentages and derived statistics from all public representations.

### S08.B — Render offline outputs

Implement Jinja2 autoescaped HTML, packaged local CSS, contents links, print layout and versioned JSON. Use structured checks rather than recomputing statistics in templates.

### S08.C — Test adversarial content and writes

Test malicious tags/formulas, raw-ID leakage, hidden JSON, overwrite refusal, atomic writes and missing assets. Review real rendered fixture HTML for readability and explicit incomplete coverage.

## Required deliverables

- write_report with safe defaults
- Offline HTML/CSS templates
- Privacy projection
- Security/layout tests and actual rendering evidence

## Acceptance gates

- No raw identifiers/paths in default outputs
- No external network assets or script execution
- Suppressed information is not recoverable from hidden report data
- Unknown checks remain prominent even for clean splits

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S08-01 | Default ID redaction | Markers absent from HTML and public JSON. |
| AT-S08-02 | Path redaction | Full path/username absent from default reports. |
| AT-S08-03 | Domain aliasing | Default report uses local aliases without reverse map. |
| AT-S08-04 | Small-cell suppression | Suppressed cell, totals, percentages and derived statistic absent from exported section. |
| AT-S08-05 | Hidden payload leakage | No suppressed values reappear in hidden markup/JSON. |
| AT-S08-06 | HTML injection | Rendered as escaped text; no script execution. |
| AT-S08-07 | Formula export | Optional human spreadsheet export neutralizes formulas. |
| AT-S08-08 | No network render | Complete layout and content without external assets. |
| AT-S08-09 | Explicit sensitive export | Sensitive banner and clearly different output; never silently enabled. |
| AT-S08-10 | Atomic write failure | Prior valid report remains intact; no unrelated deletion. |
| AT-S08-11 | Overwrite refusal | Clear refusal instead of clobbering. |
| AT-S08-12 | Coverage visibility | Missing checks remain visibly incomplete, not all-green safe. |
| AT-S08-13 | Rendering does not recompute | Rendering succeeds from precomputed record alone. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S08.md` using the handoff template. Set S08 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No web service, JS dashboard, trust score or anonymization guarantee.
