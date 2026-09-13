# S01 — Typed models, configuration and serialization contracts

**Requirement:** REQ-S01

**Entry gate:** S00 must be accepted, or an explicit human waiver must explain why its completed outputs are sufficient.

## Objective

Implement stable records and strict, offline schema validation before downstream modules create their own data formats.

## Required reading

Read root AGENTS.md and state/PROJECT_STATUS.json, then open:

- `spec/01_scientific_contract.md`
- `spec/03_architecture.md`
- `spec/04_inputs_configuration.md`
- `spec/05_models_serialization.md`
- `spec/20_contract_clarifications.md`
- `qa/acceptance_cases.json` entries whose stage is S01
- `qa/rule_catalog.json` entries relevant to these modules

## Execution prompt

Implement **S01 only** according to the files above. First inspect the existing implementation and current git diff. State the exact intended files and acceptance checks. Do not replace the project with a fresh generated codebase. Work through the following bounded packages in order; after each package run its focused tests before proceeding.

### S01.A — Implement records and errors

Create typed records, enums and documented exceptions. Define configuration parsing and optional defaults. Treat JSON duplicate keys, unknown keys, booleans-as-integers and incompatible schema versions explicitly.

### S01.B — Implement serialization

Load standalone packaged schemas locally. Implement canonical JSON utilities, private versus public result boundaries, standard null behavior and model round trips. Keep clinical and provenance claims scoped.

### S01.C — Bind tests to contracts

Exercise bundled valid/invalid contract examples; reject illegal status/evidence combinations where semantic checks are required. Document fields and no-mutation behavior. Do not implement an alternative hidden config language.

## Required deliverables

- Typed public records and errors
- Packaged schemas with offline loader
- Config/default validation
- Contract and serialization tests

## Acceptance gates

- Unknown keys and duplicate JSON keys fail
- NaN and Infinity cannot appear in emitted JSON
- Schema validation does not perform HTTP requests
- Public and operational serializers are visibly separate

## Exact acceptance cases

| ID | Case | Required outcome |
|---|---|---|
| AT-S01-01 | Unknown config key | ConfigurationError names the unsupported key. |
| AT-S01-02 | Duplicate JSON keys | Loader rejects it before last-value-wins parsing. |
| AT-S01-03 | Boolean integer ambiguity | Validation fails rather than interpreting true as 1. |
| AT-S01-04 | Optional defaults | Defaults are null and 128 respectively; no hidden role inference. |
| AT-S01-05 | Unknown schema version | Clear incompatible-version error; no best-effort reinterpretation. |
| AT-S01-06 | JSON null semantics | value=null and a non-empty reason; never NaN. |
| AT-S01-07 | No Infinity output | Reject or explicitly map to a reasoned null at the metric boundary. |
| AT-S01-08 | Offline schema validation | No HTTP/schema download; supported examples validate. |
| AT-S01-09 | Record round trip | All schema-defined meanings, enums and ordering are preserved. |
| AT-S01-10 | Config immutability | No silent mutation of user settings. |
| AT-S01-11 | Private/public separation | Public projection omits private IDs/digests; operational format is visibly sensitive. |

## Verification and stop condition

Run the applicable new tests, affected predecessor tests, formatting/lint and type checks that exist at this stage. From S14 onward include the strict documentation build; at S16 include build and clean-wheel checks. Record exact commands/exit codes and actual counts. A test not run is NOT RUN, never assumed passed. Update the case-to-test/evidence mapping. Review the final diff for scientific boundary changes and sensitive content.

Write `state/handoffs/S01.md` using the handoff template. Set S01 to READY_FOR_REVIEW only when the stage's required checks passed; otherwise mark BLOCKED/IN_PROGRESS with the precise outstanding item. Human acceptance remains separate. End with files changed, checks actually run, failures/limits, and the next stage. Do not proceed automatically.

## Out of scope

No data ingestion heuristics, auditing algorithms or estimator fitting.
