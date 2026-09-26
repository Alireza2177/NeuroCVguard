# S12 instruction loading and boundary

Opened AGENTS.md, START_HERE.md, state/PROJECT_STATUS.json,
prompts/S12_comparison.md (via prompts/S12*), specification chapters
01, 07, 11, 12, 14 and 20, all nine S12 acceptance cases, the full rule catalog,
templates/HANDOFF.md, templates/ADR.md and state/handoffs/S11.md. Inspected
comparison/private-evaluation schemas, models, evaluator, split checks, CLI,
reporting/projection/template code and relevant predecessor tests. Git status and
diff were clean; HEAD was 6acfed4, the merged S10–S11 implementation.

No human-accepted handoff exists. The user explicitly requested S12 following
completed S11 and its 536 passing tests; this authorizes continuation without
claiming scientific review or changing acceptance flags. The user separately
approved the compatible optional comparison-context extension in ADR-S12-001.

Planned changes: comparison.py, _diagnostics.py, models.py, __init__.py,
_evaluation_inputs.py, evaluation.py, rules.py, _projection.py, cli.py and
templates/report.html; focused comparison/diagnostic/CLI/migration tests;
comparison/evaluation/CLI docs and README. Extend only approved comparison
context in normative/packaged standalone and embedded schemas and spec20;
regenerate reading editions. Update S12 evidence, QA/status, assistance and handoff.

Work order: A comparison algebra, private input validation and context; B narrow
diagnostic eligibility and observation-OOF participant pooling; C CLI, reporting,
privacy and integration. Run focused tests before each package transition, then
full strict pytest, doctests, Ruff, mypy and editable/ordinary installed journeys.
S13 and subsequent stages are not authorized. Baseline captures 699 existing files.

Also opened the user's original pasted-text attachment during final review. Its
initial S00-only authorization is superseded by the subsequent explicit S12
request; its preservation, truthful evidence and no-publication rules remain
consistent with the repository instructions. No skill or subagent was used.
