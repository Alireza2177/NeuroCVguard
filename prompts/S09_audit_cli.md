# S09 — CLI and usable audit milestone

**Requirement:** REQ-S09

**Entry gate:** S08 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Expose the completed audit functionality through a coherent command-line workflow.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/03_architecture.md`
- `spec/04_inputs_configuration.md`
- `spec/05_models_serialization.md`
- `spec/13_reports_privacy.md`
- `spec/14_interfaces.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S09
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S09 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S09.A — Add implemented commands

Implement init, validate, audit, split and report over existing APIs. Implement version/help and module/console parity. Do not advertise unfinished evaluate/demo/compare commands as operational.

### S09.B — Control output and exit status

Add fail-on policy, stderr logging, sanitized error messages, overwrite/sensitive flags and documented exit codes. Announce identity-bearing split exports.

### S09.C — Exercise a user journey

Run config validation, cohort audit, split generation and split audit on the fixture in a temporary directory. Verify API/CLI results agree and record actual command output.

## Required deliverables

- Working audit CLI
- End-to-end audit smoke test
- User-facing help/error contracts
- Audit milestone handoff

## Acceptance gates

- Console and python -m behavior agree
- Report is written before an audit-threshold exit 3
- Malformed input gives exit 2, not a fake report
- No success claim for not-yet-implemented baseline features

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S09-01 | CLI/module parity | Equivalent help, version, findings and exit semantics. |
| AT-S09-02 | Init is editable | Valid documented JSON without pretending to detect user columns. |
| AT-S09-03 | Audit threshold exit | Report written, then exit 3. |
| AT-S09-04 | Malformed config exit | Exit 2 with sanitized actionable message. |
| AT-S09-05 | Fail-on none | Same findings, exit 0 after successful audit; not a changed verdict. |
| AT-S09-06 | Streams separation | Progress on stderr; final paths/summary on stdout. |
| AT-S09-07 | Sensitive split announcement | CLI warns that operational files contain IDs. |
| AT-S09-08 | Unimplemented commands | No unsupported feature falsely advertised as working. |
| AT-S09-09 | API/CLI equivalence | Same projected check values excluding transient provenance. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S09.md` using the handoff template. Set S09 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No full v0.1.0 release claim yet; no publication actions.
