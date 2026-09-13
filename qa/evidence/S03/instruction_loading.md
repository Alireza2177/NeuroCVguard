# Actual S03 instruction sources

Opened during this task:

- Root `AGENTS.md`, `START_HERE.md`, `state/PROJECT_STATUS.json` and
  `prompts/S03_identity_cohort.md`.
- Every S03 required chapter: `spec/01_scientific_contract.md`,
  `spec/04_inputs_configuration.md`, `spec/06_identity_audits.md`,
  `spec/20_contract_clarifications.md`; also `spec/03_architecture.md`.
- S03 entries in `qa/acceptance_cases.json`, `qa/requirements.json` and
  `qa/rule_catalog.json`; existing `qa/case_to_test_map.json` and register baseline.
- `templates/HANDOFF.md`, the latest `state/handoffs/S01.md`,
  `state/STAGE_MAP.md`, and stage-plan inventory. No accepted handoff exists;
  S00 and S01 were READY_FOR_REVIEW, both with human acceptance false.
- `fixtures/manifest.json`, `fixtures/known_answers.json`, `fixtures/README.md`,
  the clean, changing-target and cross-site synthetic cohorts, and the clean
  split fixture through its known-answer test. No real research data were used.
- Existing models/configuration, serialization/projection boundaries, package
  metadata, README, assistance record and relevant test/evidence helpers.

The user explicitly selected S03 only after S01 and prohibited moving onward.
Inspection found S02 NOT_STARTED, no S02 handoff and no application `io.py`.
S03's prompt normally requires completed/accepted S02 or a human waiver. The
direct user stage selection takes precedence over the default sequence; it is
recorded as an implementation-order instruction, not fabricated S02 completion,
acceptance, or a human review rationale. S03 was implemented against already
constructed S01 Cohort objects. S02 ingestion integration remains NOT RUN.
The user was told this boundary before S03 implementation proceeded.

No skill was applied, no subagent was used and no external research source was
needed. Git status returned exit 1 because this directory is not a Git repository;
no Git mutation occurred. A guessed stage_graph filename was absent; inspection
located the supplied STAGE_MAP/stage_plan files instead. Pre-edit hashes of 213
existing files and exact QA/status baselines are in `baseline.json`.

No normative scientific contract conflict was found. No ADR or invented human
approval was added. Only S03 code and its documentation/tracking were changed.
