# S11 sources and scope

Opened AGENTS.md, START_HERE.md, state/PROJECT_STATUS.json,
prompts/S11_nested_tuning.md, spec/01_scientific_contract.md,
spec/05_models_serialization.md, spec/07_split_auditing.md,
spec/08_split_generation.md, spec/10_preprocessing_provenance.md,
spec/11_evaluation.md and spec/20_contract_clarifications.md. Opened the nine
S11 acceptance cases, REQ-S11, the rule catalog, templates/HANDOFF.md and
state/handoffs/S10.md. Also read the original attached implementation request;
the subsequent explicit S11 request supplies the current stage scope.

No human-accepted handoff exists. The explicit request to proceed authorizes
using completed S10 outputs (508 passing tests plus recorded checks) as the
prerequisite; it does not establish human acceptance. No acceptance flag changed.
Reviewed the existing git diff and evaluator, planner, boundary, model/schema,
projection and test implementations before extending them. The preservation
baseline contains 653 existing files, including uncommitted S10 work.

Intended production changes: new _inner_plans.py and _tuning.py; extend
_evaluation_inputs.py, _evaluation_fits.py, evaluation.py; refresh evaluation
descriptions in CLI/root API/planner and safe report limitations as needed.
Add focused inner-plan, candidate-selection and nested integration tests.
Evolve the prior S10 tune-refusal case to S11 tune support while retaining the
other scope guards. Update docs/evaluation.md, docs/cli.md, README.md,
AI_ASSISTANCE.md, S11 QA/status/evidence and handoff. No normative schema or
scientific contract change is intended.

Check each bounded package before proceeding: A inner memberships and preflight;
B candidate fits and pooled/tie semantics; C refit/isolation/failure/CLI. Then
full strict pytest, doctests, Ruff lint/format and mypy. Exercise local editable
and ordinary installed CLI paths. S12 and all later stages remain untouched.
