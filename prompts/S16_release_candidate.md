# S16 — Build, clean installation and release-readiness dossier

**Requirement:** REQ-S16

**Entry gate:** S15 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Prove that the complete package, not just the source tree, is ready for a controlled public release.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/00_project_charter.md`
- `spec/03_architecture.md`
- `spec/05_models_serialization.md`
- `spec/13_reports_privacy.md`
- `spec/14_interfaces.md`
- `spec/16_quality_tests.md`
- `spec/17_documentation.md`
- `spec/18_security_release.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S16
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S16 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S16.A — Distributions

Build wheel/sdist, validate metadata, inspect package files and verify templates/schemas/demo resources. Check version consistency and hashes.

### S16.B — Clean installs and CI

Install the wheel outside the repo; run import/CLI/demo and core tests. Exercise the required CI matrix or state which platforms remain unverified. No editable-source fallback.

### S16.C — Dossier and human gates

Assemble actual tests/build/docs/privacy evidence, unresolved risks and public metadata checklist. Set local candidate ready-for-review, never auto-approve a public release.

## Required deliverables

- Validated distribution artifacts
- Clean-install evidence
- Release dossier and checklist
- Recorded owner/security/citation/publication gates

## Acceptance gates

- Wheel demo works with no source-tree access
- All runtime assets included; private data excluded
- Actual supported platform matrix is truthful
- No external publication has occurred implicitly

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S16-01 | Build distributions | Both valid and metadata checks pass. |
| AT-S16-02 | Wheel resource list | Schemas/templates/CSS/demo assets included; private files excluded. |
| AT-S16-03 | Clean wheel execution | Import, CLI and demo work without source-path fallback. |
| AT-S16-04 | Cross-platform matrix | Evidence records only actual passes; unavailable platforms remain pending. |
| AT-S16-05 | Lowest dependency check | No unsupported bound is advertised. |
| AT-S16-06 | Release hashes | Dossier records matching version/files/SHA256. |
| AT-S16-07 | No unresolved result bug | Result-changing defects block readiness. |
| AT-S16-08 | No unauthorized release | No push/upload/tag/DOI operation without explicit authorization. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S16.md` using the handoff template. Set S16 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No public push/tag/upload/DOI creation without S17 authorization.
