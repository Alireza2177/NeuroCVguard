# S11 — Nested participant-aware regularization selection

**Requirement:** REQ-S11

**Entry gate:** S10 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Add a small correct inner selection loop without consuming any outer-test information.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/05_models_serialization.md`
- `spec/07_split_auditing.md`
- `spec/08_split_generation.md`
- `spec/10_preprocessing_provenance.md`
- `spec/11_evaluation.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S11
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S11 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S11.A — Inner plans

Use supplied valid inner folds or generate participant/component-disjoint inner folds from outer training only. Capture generated memberships in a derived run record.

### S11.B — Candidate evaluation

Fit fresh pipelines for each C/inner fold; compute pooled inner participant balanced accuracy; use the same memberships for every C. Implement exact tie-breaking.

### S11.C — Refit and verify

Refit a fresh chosen pipeline on outer train, then predict outer test. Add adversarial spies, infeasibility tests and proof that a failing inner run does not silently fall back.

## Required deliverables

- tune=true path
- Candidate/selection provenance
- Nested isolation tests
- Documentation of inner versus outer objective

## Acceptance gates

- Outer test never participates in candidate selection
- Inner validation never reaches inner fit
- Ties select smallest C within 1e-12
- All candidates share memberships and fresh estimator objects

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S11-01 | Inner fit spy | Inner validation and outer test absent from all fit calls. |
| AT-S11-02 | Outer-test choice independence | Chosen C remains unchanged for that outer fold. |
| AT-S11-03 | Same candidate memberships | Exact same folds across candidate values. |
| AT-S11-04 | Fresh candidate fits | Independent clones, no fitted-state carryover. |
| AT-S11-05 | Tie rule | Smallest numeric C selected. |
| AT-S11-06 | Pooled participant objective | Selection uses pooled participant balanced accuracy, not row-weighted mean fold accuracy. |
| AT-S11-07 | Infeasible inner groups | Tuning fails explicitly; no default-C fallback. |
| AT-S11-08 | Refit boundary | Fresh fit on all and only outer train. |
| AT-S11-09 | Original plan immutability | Original plan unchanged; derived run records actual inner memberships. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S11.md` using the handoff template. Set S11 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No broad AutoML, score-based seed hunting or outer-test early stopping.
