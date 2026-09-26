# ADR-S10-001 — Retain the evaluated plan in private results

Date: 2026-09-26
Status: APPROVED by explicit user decision in this task

## Conflict and concrete counterexample

spec/11_evaluation.md §11.8 requires a plan digest and actual folds in the
structured evaluation result. The original evaluation-result schema has no
plan digest or test memberships; each fold only has status/counts/metrics,
and provenance has additionalProperties=false. For example, adding
`plan_digest` to the supplied evaluation_schema_example.json fails the original
schema's additionalProperties rule. No available field can encode an exact
plan without misusing its documented meaning. The affected output work was
paused while preflight preparation continued.

## Decision and authorization

The user answered “Approve compatible schema extension (Recommended)” to adding
optional `plan_digest` and `actual_plan` fields populated by the S10 runner.
`actual_plan` embeds the standalone split-plan contract. `plan_digest` hashes its
canonical operational dictionary. Both are present together or absent together.
The evaluator always supplies both, including on incomplete runs. They remain
private and do not change the public report schema.

Existing private schema 1.0 records without either field remain readable by the
updated library. Older readers with the original closed schema will reject new
extended records; update the reader instead of discarding fields. No old fixture
or history is rewritten to pretend it contained this information.

## Consequences and validation

Update normative and packaged evaluation schemas, typed record validation,
specification clarification and generated reading editions. Add migration and
digest/membership alignment tests. This decision authorizes only the stated
contract extension, not tuning, diagnostic overlap evaluation, human acceptance
of S10 or public release. No scientific threshold or rule meaning changes.
