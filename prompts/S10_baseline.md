# S10 — Fixed-parameter controlled evaluator

**Requirement:** REQ-S10

**Entry gate:** S09 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Implement the auditable fixed-C classification runner and exact participant-level metric semantics.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/05_models_serialization.md`
- `spec/07_split_auditing.md`
- `spec/10_preprocessing_provenance.md`
- `spec/11_evaluation.md`
- `spec/14_interfaces.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S10
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S10 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S10.A — Preflight and pipeline

Validate complete one-repeat CV, constant participant targets, roles and training classes. Construct the prescribed imputer/scaler/logistic Pipeline and participant-loss weights.

### S10.B — Execute observed fits

Clone per fold; record actual fit boundaries; handle convergence and fitting failures. Predict only held-out rows with explicit class-order mapping. Keep upstream limitations.

### S10.C — Aggregate and expose

Average probabilities per participant, compute exact metric/null rules, write private evaluation and public reports. Add evaluate CLI. Test fixed probability oracles and an independent fit-spy.

## Required deliverables

- evaluate_baseline tune=false
- Private EvaluationResult and public summary
- Metric/reference tests
- Evaluate CLI and real synthetic run evidence

## Acceptance gates

- No outer-test row reaches a fit call
- Undefined metrics are null with reasons
- Any failed fold prevents a complete pooled score
- One-off/repeated/longitudinal-unstable designs are explicitly refused

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S10-01 | Training-only scaler | Fitted scaler statistics match train-only reference, not all data. |
| AT-S10-02 | Fit ID spy | Only current training IDs observed. |
| AT-S10-03 | Fresh estimator objects | No shared fitted state or reused fitted pipeline. |
| AT-S10-04 | Participant loss weights | Classifier weights sum to one for each participant. |
| AT-S10-05 | Probability aggregation | Participant prediction derives from mean probabilities, not majority votes. |
| AT-S10-06 | Probability class ordering | Mapped probabilities/metrics agree with declared class labels. |
| AT-S10-07 | All-missing training feature | Documented imputer handling and diagnostic; no global imputation. |
| AT-S10-08 | Constant-target limit | UnsupportedDesignError rather than baseline relabeling. |
| AT-S10-09 | Single-class test AUC | AUC and class-complete metrics null with reasons; accuracy still available. |
| AT-S10-10 | Positive class unspecified | Binary AUC null with explicit reason; other metrics computed. |
| AT-S10-11 | Metric oracle | Accuracy, class recall and complete-class metrics match independent calculations. |
| AT-S10-12 | Convergence failure | Failed fold/run status, no complete pooled score. |
| AT-S10-13 | No easy-fold average | No pooled complete-CV metric presented. |
| AT-S10-14 | Scope guards | Explicit refusal; partition audit remains available. |
| AT-S10-15 | Private/public outputs | Sensitive private result separate from sanitized report pair. |
| AT-S10-16 | No model deserialization | Refusal without execution. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S10.md` using the handoff template. Set S10 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No tuning until S11, arbitrary models, calibrated clinical claims or inferential intervals.
