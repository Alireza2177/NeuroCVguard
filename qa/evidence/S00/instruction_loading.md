# S00 instruction loading and initial inspection

Date: 2026-09-13. Reader/implementer: Codex (AI agent). Stage: S00 only.

The project root is the directory containing AGENTS.md, START_HERE.md,
spec/, prompts/, contracts/, qa/ and state/. No nested project was created.

Actually opened before implementation:

- The user's attached `pasted-text.txt` request (S00.A–C authorization).
- `AGENTS.md` (the only AGENTS.md found in the project).
- `START_HERE.md`.
- `state/PROJECT_STATUS.json`: target 0.1.0, S00 selected, all stages NOT_STARTED.
- `prompts/S00_bootstrap.md`.
- `spec/00_project_charter.md`.
- `spec/01_scientific_contract.md`.
- `spec/02_execution_governance.md`.
- `spec/03_architecture.md`.
- `spec/18_security_release.md`.
- `spec/20_contract_clarifications.md`.
- `qa/acceptance_cases.json`: all five S00 entries.
- `qa/rule_catalog.json`: all entries inspected; none applies to S00.
- `qa/case_to_test_map.json`: initially empty mappings.
- `templates/HANDOFF.md`.
- `templates/AI_ASSISTANCE_RECORD.md`.
- `spec/17_documentation.md`: additional source for the proposed BSD-3-Clause
  license and truthful AI-assistance record; no S14 work authorized or implemented.
- `qa/requirements.json`: REQ-S00 entry.
- `state/stage_plan.json`: S00 entry and specification mapping.
- `tools/validate_foundation.py`: initial section inspected; its initial-state
  assertions are foundation-only, not post-implementation application checks.

`Get-ChildItem state -Recurse -File` found no existing handoff or decision
records. There is no accepted predecessor handoff for this initial stage.
`rg --files -g AGENTS.md` found only the root instructions. The assembled
master/HTML are preserved reading editions, not alternate technical sources.

Git is installed, but `git status --short` failed: this directory is not a
Git repository. `git diff` and `git diff --stat` likewise could not provide
a repository diff. No git initialization, staging, reset, clean, or remote
operation was performed. A SHA-256 inventory of all 91 pre-existing files is
saved in `baseline.json`. These files were all untracked local work, including
unrelated foundation material. Their bytes were checked unchanged immediately
after creating state/handoffs, state/decisions, and qa/evidence/S00 (exit 0).
Git-index preservation is not applicable because there is no index.

The implemented boundary is an installable package with import, help and
version only. Future research behavior must distinguish repeated observations
from train/test overlap, protect participant/dependence components, condition
domain separation on the objective, and leave unknown preprocessing
unassessable. No auditing, splitting, fitting, reporting, patient-data access,
clinical claim, or scientific validity verdict is implemented here.

Instruction loading and metadata review are AI evidence, not human acceptance.
