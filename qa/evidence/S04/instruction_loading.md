# Actual S04 instruction sources

Opened during this task:

- Root `AGENTS.md`, `START_HERE.md`, `state/PROJECT_STATUS.json` and
  `prompts/S04_split_audits.md`.
- Every S04 required chapter: `spec/01_scientific_contract.md`,
  `spec/04_inputs_configuration.md`, `spec/05_models_serialization.md`,
  `spec/07_split_auditing.md` and `spec/20_contract_clarifications.md`.
- `spec/14_interfaces.md`; relevant diagnostic context in
  `spec/12_design_comparison.md`, privacy sections 1-6 of
  `spec/13_reports_privacy.md` and relevant `spec/03_architecture.md` content.
- Full `contracts/split-plan.schema.json`; relevant strict AuditReport
  input_summary/provenance/result_type definitions in `contracts/audit-report.schema.json`.
- S04 entries in `qa/acceptance_cases.json`, `qa/requirements.json` and
  `qa/rule_catalog.json`; existing `qa/case_to_test_map.json` and exact baseline registers.
- `templates/HANDOFF.md` and full latest `state/handoffs/S03.md`. No accepted
  handoff exists: S00, S01 and S03 remain READY_FOR_REVIEW with human acceptance false.
- Existing models/configuration, identity/inventory, serialization/projection,
  rules, root imports, bootstrap tests and evidence helpers. Synthetic clean,
  leaky and unknown split fixtures and cohort fixtures were loaded by focused
  tests; the clean plan and assignment headers were also inspected directly.

The latest direct user instruction selects S04 only and prohibits automatic
progression. The prompt's normal S03 human-acceptance entry gate is still pending.
The direct instruction authorizes this bounded implementation; it is not recorded
as a fabricated acceptance, review or human waiver rationale. Completed S03
inventory/component outputs and the passing predecessor regressions support the
in-memory API work. All existing human acceptance flags remain unchanged.

S02 is NOT_STARTED and no S02 handoff exists. The S04 binding requirement needs
only the minimal mapped-metadata digest over an existing S01 Cohort. This task
implements that dependency, without cohort/feature file loading, joins or a
feature digest. S02 integration remains NOT RUN. The user was informed of the
stage and in-memory boundary during implementation.

No skill was applied, no subagent was used and no external research source was
needed. Git status returned exit 1 because the folder is not a Git repository;
no Git mutation occurred. Pre-edit hashes of 260 files and exact status/register
baselines are in `baseline.json`. No normative conflict was found or hidden;
no ADR or human approval was invented.
