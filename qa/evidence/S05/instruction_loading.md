# Actual S05 instruction sources

Opened during this task:

- Root AGENTS.md, START_HERE.md, state/PROJECT_STATUS.json and
  prompts/S05_split_generation.md.
- All required chapters: spec/01_scientific_contract.md,
  spec/05_models_serialization.md, spec/06_identity_audits.md,
  spec/07_split_auditing.md, spec/08_split_generation.md and
  spec/20_contract_clarifications.md. Split generation and clarifications were
  reopened separately after combined tool output truncation.
- spec/14_interfaces.md for exact make_splits and SplitPlan.write boundaries;
  spec/03_architecture.md for dependency direction and engineering requirements.
- Full contracts/split-plan.schema.json and the seed bounds in
  contracts/config.schema.json. Read source model/configuration validation,
  identity/inventory, split audit/projection, serialization and rule definitions.
- S05 rows in qa/acceptance_cases.json, qa/rule_catalog.json and
  qa/requirements.json. Existing case-to-test mappings/statuses were parsed into
  the pre-edit baseline before adding S05 rows.
- Full latest state/handoffs/S04.md and templates/HANDOFF.md. No accepted
  handoff exists; previous implemented stages remain READY_FOR_REVIEW with
  human_accepted=false.
- Existing synthetic fixture adapter, clean cohort header, S04 evidence helpers,
  package configuration, README and assistance record. No real participant data
  was used. Targeted search across prompts/spec found spec/11_evaluation.md's
  inner-generation boundary and prompts/S11_nested_tuning.md's scope; these
  matching passages, not the full later-stage documents, were read.

The latest user instruction explicitly selects step 5 and prohibits continuing.
This authorizes S05 implementation without inventing human acceptance of S04.
The normal human-review entry gate remains pending; completed S04 auditing and
its passing regression evidence supply the dependency used here. No previous
acceptance flag or human waiver rationale is fabricated. S02 remains NOT_STARTED;
S05 consumes existing constructed Cohort records and reuses S04 metadata binding.
S02 ingestion integration is NOT RUN.

S05 implements outer plans only. Requests with evaluation.tune=true are refused
explicitly; the nested-generation implementation belongs to S11 and was not
started. No S06 or later implementation was performed.

No skill, subagent or external research source was used. Git status returned
exit 1 because this directory is not a Git repository. A wildcard passed to rg
was rejected by Windows; a directory-scoped rg query then found the intended
passages. Neither command changed files. The baseline contains hashes for 311
existing files and exact project/QA registers. No normative contract conflict
was found; no ADR or fabricated approval was added.
