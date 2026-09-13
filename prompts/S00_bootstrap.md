# S00 — Repository bootstrap and environment evidence

**Requirement:** REQ-S00

**Entry gate:** None; this is the first implementation stage.

## Objective

Establish a conventional local package workspace and an exercised development environment without implementing scientific features.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/00_project_charter.md`
- `spec/01_scientific_contract.md`
- `spec/02_execution_governance.md`
- `spec/03_architecture.md`
- `spec/18_security_release.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S00
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S00 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S00.A — Inspect the repository and instructions

Read the foundation; inspect existing files and git status; preserve unrelated work. Summarize scientific scope and exclusions. Create the local state/decision/evidence directories without pretending any prior code exists.

### S00.B — Create minimal installable structure

Create src/neurocvguard with version and module entry point, pyproject.toml, pytest configuration and a minimal import test. Select the prescribed dependencies, install in a virtual environment, record actual versions and interpreter. Do not advertise future subcommands.

### S00.C — Establish hygiene

Add focused .gitignore, formatter/type-check configuration, a truthful development README and proposed license metadata. Publication-specific identity/URL/name fields remain explicitly pending, not guessed. Record environment problems as blocked evidence.

## Required deliverables

- Installable minimal source package
- Environment/compatibility record
- Import smoke test and lint/type configuration
- S00 handoff; all later stages not started

## Acceptance gates

- Fresh environment imports the package without filesystem/network side effects
- Editable install and the import smoke test actually run
- No fabricated repository, PyPI, DOI or CI badge
- AGENTS is loaded and the stage maps to the correct specs

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S00-01 | Import has no side effects | No new files, worker processes, network calls or dataset access. |
| AT-S00-02 | Editable installation | Import and the version entry point work using declared dependencies. |
| AT-S00-03 | Preserve unrelated work | Bootstrap does not overwrite, remove or stage that file automatically. |
| AT-S00-04 | Truthful metadata | No false PyPI link, DOI, supported-platform claim or passing-CI badge. |
| AT-S00-05 | Instruction loading | It identifies AGENTS, current stage and relevant specifications actually read. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S00.md` using the handoff template. Set S00 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No audits, classifiers, GUI, public push, package upload or large generated source tree.
