# S17 — Human-approved public release and maintenance handoff

**Requirement:** REQ-S17

**Entry gate:** S16 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Publish only the reviewed artifacts after explicit owner authorization and then verify the public installation.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/02_execution_governance.md`
- `spec/17_documentation.md`
- `spec/18_security_release.md`
- `spec/19_research_roadmap.md`
- `spec/20_contract_clarifications.md`
- `spec/21_sources.md`
- `qa/acceptance_cases.json` entries whose stage is S17
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S17 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S17.A — Owner and metadata checkpoint

Confirm real maintainer identity/contact, copyright, license, namespace availability, public repository visibility and exact release commit. Record consent for each external action.

### S17.B — Approved publication

Publish the approved repository/tag/release and package through least-privilege workflows. Register an archive/DOI only if authorized; insert only actual identifiers. Never manufacture historical activity.

### S17.C — Independent verification and maintenance

Verify install from the real published distribution in a clean environment; check docs and citation links; record release evidence and known limitations. Open maintenance tasks based on actual findings.

## Required deliverables

- Actual public release, only if authorized
- Verified public installation
- Accurate citation/release metadata
- Maintenance and optional research backlog

## Acceptance gates

- No invented authorization or public identifier
- Published bytes/version match reviewed release
- AI assistance and human review described truthfully
- Publication or DOI failure is reported as incomplete, not success

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S17-01 | Publication authorization | No fabricated approval; missing approval leaves stage blocked. |
| AT-S17-02 | Namespace ownership | Available/owned names verified; conflicts handled transparently. |
| AT-S17-03 | Published artifact identity | Match or explicit explanation; no silent rebuild with different contents. |
| AT-S17-04 | Public fresh install | Version/import/demo verified or release marked incomplete. |
| AT-S17-05 | Citation link validity | Only real working identifiers appear in citation metadata. |
| AT-S17-06 | Honest development history | No manufactured dates, users, reviews or adoption claims. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S17.md` using the handoff template. Set S17 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No automated journal submission, artificial user activity or promise of research publication.
