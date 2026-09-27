# ADR-S15-002 — Explicit foundation validation scope

Status: implemented within the user's S14/S15 follow-up request to apply the most
logical and defensible approach. This is a tooling decision, not a waiver of a
scientific requirement, human acceptance, or authorization for another stage.

The old standalone validator crashed on Windows because native backslash schema
keys disagreed with forward-slash manifest keys. It also required an untouched,
unimplemented repository and always overwrote qa/foundation_validation.json with
a hardcoded NOT_IMPLEMENTED claim. Those assumptions cannot certify the current
implemented repository. The prior failure and historical record remain intact.

Use portable schema keys. Preserve all three original snapshot assertions in the
default foundation mode. Add explicit artifacts mode for the shared structural,
schema and known-answer checks; list the snapshot checks as outside that scope,
never as passed. Both modes report zero application tests executed and the actual
recorded software status, without validating its truth or human acceptance.

Print by default and write only a new explicitly named output using exclusive
creation. Reset in-memory checks between calls. A malformed known-answer split
with unknown IDs must report failure rather than crash during participant lookup.
Regression tests cover both modes, Windows spelling, corrupted fixtures, output
preservation and repeated invocation. The repaired validator is now included in
ordinary Ruff checks; the previous legacy exclusion is removed.

Do not change the scientific package, accepted first-import limitation, quality
thresholds, historical records, human-review flags or S16/S17 status. The original
default still fails on the implemented repository for its three intended snapshot
conditions. Use the explicit artifact check alongside, never instead of, pytest,
coverage, strict docs, scientific review and future release checks.
