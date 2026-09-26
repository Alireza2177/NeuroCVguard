# S09 instructions actually opened

Read AGENTS.md, START_HERE.md, state/PROJECT_STATUS.json,
prompts/S09_audit_cli.md, spec/03_architecture.md,
spec/04_inputs_configuration.md, spec/05_models_serialization.md,
spec/13_reports_privacy.md, spec/14_interfaces.md and
spec/20_contract_clarifications.md. Reopened required chapters when combined
terminal output was truncated. Read all nine S09 acceptance entries in
qa/acceptance_cases.json and inspected qa/rule_catalog.json (no S09-specific rule).
Opened templates/HANDOFF.md and the latest completed handoff state/handoffs/S08.md.
No human-accepted handoff exists. The user's explicit request to proceed is
implementation authorization; it does not mark any stage ACCEPTED.

S02 was absent. The user explicitly chose “Complete S02, then S09” in response to
the prerequisite question. S02's own reading, implementation and verification are
recorded in qa/evidence/S02 and state/handoffs/S02.md. S09 starts from that
completed local prerequisite. Its baseline contains 556 preexisting files.

Opened relevant configuration, records, input, identity, split, provenance,
serialization, privacy and reporting implementations and their tests, as well as
fictitious fixture contracts. No normative schemas or scientific rules were edited.
No external lookup, skill or delegated agent was used. No real participant data,
public upload, publication or acceptance action was involved.

Planned scope: cli.py and module dispatch; lazy root load_config; shared workflows
and configured report writing; three CLI test modules; bootstrap expectation
updates; CLI documentation, README, assistance record and S09 QA/state/handoff.
AT-S09-01–09 cover parity, editable init, threshold ordering, malformed input,
unchanged findings under fail-on none, streams, sensitive exports, absent future
commands and API equivalence. Packages A, B and C were tested in that order.
