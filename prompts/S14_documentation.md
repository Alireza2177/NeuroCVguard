# S14 — Complete documentation and contributor materials

**Requirement:** REQ-S14

**Entry gate:** S13 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Make the complete tool understandable and maintainable without reading implementation details.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/00_project_charter.md`
- `spec/01_scientific_contract.md`
- `spec/14_interfaces.md`
- `spec/15_synthetic_examples.md`
- `spec/16_quality_tests.md`
- `spec/17_documentation.md`
- `spec/18_security_release.md`
- `spec/20_contract_clarifications.md`
- `spec/21_sources.md`
- `qa/acceptance_cases.json` entries whose stage is S14
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S14 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S14.A — User docs

Write the README, installation/troubleshooting, quickstart, input/config/CLI/API references and all required methodological interpretation pages.

### S14.B — Contributor/governance docs

Add contribution/testing/release guidance, changelog, proposed license, code of conduct, issue/PR templates and honest AI-assistance record. Keep unconfirmed public metadata blocked.

### S14.C — Executable consistency review

Build Sphinx strictly, run every command/script, validate links and match documented feature claims to code/tests. Prepare the maintainer ownership questions and external-user test checklist.

## Required deliverables

- Built documentation site
- Accurate README and examples
- Governance/support files
- Doc-to-code consistency evidence

## Acceptance gates

- No fake DOI/author/CI/public package claim
- Every documented public function/key exists
- Strict docs build passes
- Limitations and sensitive-output distinctions are easy to find

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S14-01 | Strict docs build | No broken references or ignored build failures. |
| AT-S14-02 | Public API coverage | All public functions/types/exceptions documented. |
| AT-S14-03 | Configuration coverage | Every key/default/type/limit described correctly. |
| AT-S14-04 | CLI help examples | Commands and option placement match implementation. |
| AT-S14-05 | Limitations discoverable | Unknown upstream provenance and scope limitations clear near usage. |
| AT-S14-06 | Metadata authenticity | No invented DOI/contact/contributor/version support. |
| AT-S14-07 | AI record accuracy | No hidden/fabricated authorship or exhaustive review claims. |
| AT-S14-08 | Maintainer walkthrough | Record actual human understanding/review or leave gate pending. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S14.md` using the handoff template. Set S14 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No invented contributors, testimonials or claims of independent review.
