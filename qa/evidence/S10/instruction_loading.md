# S10 instructions actually opened

Opened AGENTS.md, START_HERE.md, state/PROJECT_STATUS.json,
prompts/S10_baseline.md and the seven required chapters:
spec/01_scientific_contract.md, spec/05_models_serialization.md,
spec/07_split_auditing.md, spec/10_preprocessing_provenance.md,
spec/11_evaluation.md, spec/14_interfaces.md and spec/20_contract_clarifications.md.
Reopened chapters when combined terminal output was truncated. Read all 16 S10
acceptance cases and the rule catalog, including the four S10 rule definitions.

Opened state/handoffs/S09.md, templates/HANDOFF.md and templates/ADR.md. No accepted
handoff exists: prior stages are READY_FOR_REVIEW with human_accepted=false. The
user explicitly authorized proceeding to S10; this is implementation authorization,
not an assertion that human scientific review or acceptance occurred.

Inspected current diff and Git status: initially clean at
f2d995ded431404089eae8f5faca9379b6241f89. The preservation baseline has 595 existing
tracked/unignored files. Opened relevant cohort/config/input, split audit,
fit-boundary, record/schema, privacy, report writer and CLI implementations, tests
and fictitious fixtures. Inspected installed sklearn constructor signatures rather
than copying deprecated parameters.

Identified the plan-provenance/schema conflict before implementing affected
outputs. The user explicitly approved paired optional plan_digest/actual_plan
fields. ADR-S10-001 records the counterexample, approval, exact extension and
migration. The contract check reproduces the original closed-schema failure and
verifies that no other schema property changed. Read tools/build_master.py before
regenerating the derived reading editions after the approved normative amendment.

Planned files: evaluator preflight/fits, metrics and public evaluator API; CLI,
private/public writer, rule wording/projection, five evaluation test modules,
evaluation guide, stage evidence/status and handoff. Selected checks cover
AT-S10-01 through AT-S10-16; packages A, B and C were implemented/tested in order.
No skill, delegated agent, external research, clinical advice, patient data, public
upload, publication or later-stage implementation was used.
