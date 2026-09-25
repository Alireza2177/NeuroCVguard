# S07 implementation-agent review

Date: 2026-09-25. Reviewer: implementing Codex agent. This is not independent
review or human scientific acceptance.

Inspected the tracked diff and new provenance, preprocessing-check and fit-boundary
modules, tests and guide. Checked these boundaries:

- Imported source is strictly user_declaration; schema parsing rejects a forged
  runtime label. Strict JSON and bounded local file reads do not execute code.
- Event IDs are unique; explicit fit IDs must identify cohort observations.
  Fold references are resolved by repeat/outer/inner keys when context exists.
  Missing context remains unassessable and is never fabricated from a scope name.
- IDs outside the named training set are retained for a declared violation.
  Inner validation and outer test are excluded from inner training boundaries.
  Data-dependent all-cohort fitting produces a qualified warning, not proof of
  historical execution. External/unknown history cannot pass as verified.
- Fixed non-learning transformations receive no blanket leakage assertion;
  wording explicitly limits that conclusion to a fixed row-local conversion
  and asks for separate review of target use. The global upstream limitation
  persists under every declaration outcome, including empty ledgers and passes.
- The exact audit_cohort API has no plan argument. The documented lower-level
  check_preprocessing function handles plan-aware comparisons; audit_cohort
  leaves fold-specific comparison unresolved. Split-only auditing now uses
  the S07 warning-severity upstream rule instead of the previous info placeholder.
- FitBoundary is planning data only, with no status or observed evidence label.
  It does not create FitEvent records or call estimators. Validation accepts a
  strict training subset and refuses outside IDs; the future evaluator still
  needs scientific preflight and actual call/outcome capture. Tests construct
  handwritten synthetic records without claiming completed scientific fits.
- Public projection uses fixed declaration-qualified messages and omits private
  memberships, event names, transform names and notes. Report round trips and
  adversarial names were tested; no HTML renderer or CLI expansion was added.
- All existing tests remained unchanged and ran in the full suite. No failure
  was removed, skipped or hidden. Normative schemas, fixtures and definitions
  are unchanged; only S07 execution/implementation mappings are updated.

The first S07.B run exposed that the existing CheckResult contract disallows
unassessable evidence under NCG-PROV-003. Missing comparison context now correctly
uses NCG-PROV-001, while 003 retains declared pass/fail semantics. The affected
tests retain their unassessable assertions and now assert the explicit missing
reason. This is a rule-selection correction, not a weakened schema or test.

Initial lint/type findings were import cleanup, two long strings and a scope
annotation broader than the actual CheckResult scope. These were corrected
without new type-check exceptions. The first ordinary install could not obtain
hatchling under the restricted environment; approved retry succeeded. All failed
logs remain in the command register. Git diff --check passed with only the
repository's informational LF-to-CRLF notice.

S07 remains research-only and awaits human review. Full evaluation, ingestion,
report rendering and cross-platform/dependency-matrix validation are not claimed.
See closeout.json for preservation checks and change_inventory.json for hashes.
