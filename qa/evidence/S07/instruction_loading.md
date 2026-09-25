# Actual S07 sources opened

Date: 2026-09-25. The user selected stage 07. Only S07 is authorized in this run.

- Full AGENTS.md, START_HERE.md, state/PROJECT_STATUS.json and
  prompts/S07_provenance.md.
- All required chapters: spec/01_scientific_contract.md,
  spec/05_models_serialization.md, spec/07_split_auditing.md,
  spec/10_preprocessing_provenance.md, spec/20_contract_clarifications.md.
  Chapters 07 and 20 were reopened after combined output truncation.
- Full spec/14_interfaces.md and spec/13_reports_privacy.md for the exact
  audit_cohort signature and existing serialization boundary.
- contracts/preprocessing-ledger.schema.json; the fit_events section of
  contracts/evaluation-result.schema.json; existing LedgerEvent,
  PreprocessingLedger, FitEvent and CheckResult semantic validators.
- All S07 rows of qa/acceptance_cases.json, qa/rule_catalog.json and
  qa/requirements.json, plus parsed prior QA mappings for the hash baseline.
- Full latest state/handoffs/S06.md and templates/HANDOFF.md. No accepted
  handoff exists: prior implemented stages remain READY_FOR_REVIEW and
  human_accepted=false. No human acceptance is inferred from the new instruction.
- Existing audit, projection, rules, configuration, strict serialization,
  identity/plan context, record decoding and cohort checks; relevant existing
  contract/split tests and the synthetic ledger fixture. The initial exploratory
  read confirmed provenance.py did not exist; S07 adds that module.

The normal predecessor human-review gate remains pending. The explicit user
instruction to proceed authorizes S07 work using the completed S06 outputs,
without inventing human review or a waiver rationale. S02 is still unimplemented;
constructed Cohort records supply the input boundary. S08 and later stages are
not started. No skill, subagent, external research, notebook execution, real
participant data or public release operation was used.

Unlike the earlier handoff, the workspace now has Git history. Initial status
was clean and HEAD was 2224dfd. A pre-edit baseline records 398 existing files
and the exact project/QA registers; virtual environments, caches and build outputs
are excluded. Existing tracked changes are reviewable with git diff; new modules
were opened separately. No schemas or normative spec/rule definitions were changed.
