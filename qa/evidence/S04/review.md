# S04 implementation review

Reviewed by the implementation AI on 2026-09-13. This is neither independent nor
human review. Human acceptance remains pending; only S04 is delivered.

The review compared supplied-plan behavior with spec chapters 07 and 20, the
split schema, exact API signatures and all 17 S04 acceptance cases. No normative
schema, rule catalog, fixture or scientific requirement was edited. The strict
AuditReport shape is preserved: split eligibility is a scoped NCG-SPLIT-011
CheckResult evidence record, not an additional external envelope.

Scientific boundaries examined and exercised:

- JSON and outer-only TSV are validated before set conversion. Duplicates,
  unknown identities, objective/role mismatch and non-null digest mismatch fail
  import. Null digests bind only after membership validation; imported origin
  remains imported. Generated record integrity checks survive import.
- Metadata hashing includes the complete role mapping and canonical mapped
  records sorted by observation key. A literal JSON/hash oracle tests this
  representation. Row order and feature values do not change the binding;
  mapped metadata changes do. Missing mapped data remains explicit null.
- Literal train/test intersections distinguish observation, participant and
  transitive protected-component overlap. An independent set oracle and
  Hypothesis examples check participant/component counts. Participant-local
  sessions add explanatory evidence; repeated training use across folds is normal.
- Observation overlap remains an error even with diagnostics. Subject/component
  overlap is an error for supported objectives and a warning for audit_only;
  audit_only never produces objective validity. Diagnostics waive no S04 check.
- Shared sites are allowed for unseen_participant. Required site/phase overlap
  fails the relevant domain objective. Missing required labels stay unassessable;
  a separately observed overlap is retained rather than hidden by missingness.
- Global class order and participant support are retained internally. Missing
  training classes block the fold; missing test classes warn without fabricating
  scores. Incomplete/changing participant targets cannot become guessed labels.
- Every inner partition covers only outer training and excludes outer test.
  Observation, participant, component and exactly-once validation checks remain
  separate. Domain-held-out outer plans use an explicitly stated participant
  inner objective. Missing requested inner plans remain unassessable; nothing
  is generated or repaired. Supplied inner records are checked even if tuning
  is disabled.
- Holdouts are auditable and may be valid for the objective, but not complete
  CV. Repeats are checked independently; overall v0.1 eligibility requires one
  complete repeat. Malformed multi-fold coverage cannot use the holdout exception.
- Unknown observation membership leaves structural findings visible and dependent
  identity/domain/class checks unassessable, while other folds still run.
- The fixed unknown-upstream provenance boundary remains unassessable. Technical
  report execution is partial even when split validity passes. The split-level
  evaluation_permitted field does not claim feature availability, model execution,
  preprocessing verification or implemented downstream evaluation.

Privacy and ownership: default serialization omits raw memberships, domain/class
labels, component digests and open evidence. Repeat/fold scope labels are aliased.
Only exact booleans and nonnegative integer summary counts survive the S04
public evidence projection. Tests attempt private strings and bool-as-count
substitution. Explicit sensitive exports preserve detailed local evidence.
Inputs remain unmodified; row and fold permutation produce identical audit
results. No table output, network use, telemetry, fitting or dynamic user-code
execution was added. The repository-owned example is executed by a test only.
JUnit hostnames are replaced by LOCAL_HOST_REDACTED; outcomes, names, timings
and counts are unchanged. Evidence uses synthetic records only.

Verification: 185 full-suite tests passed (130 predecessor plus 55 S04), with no
failures/errors/skips; 7 doctests passed separately. All 17 S04 cases map to 25
actual passing nodes. Mypy passed 16 source files; lint passed after correcting
imports. The ordinary Python 3.12 package install, isolated installed-code smoke
and pip dependency check passed. Exact final formatting/preservation results and
all commands are recorded in commands.md and the stage handoff.

Retained failed attempts: the initial TSV test compared absent inner_folds=None
with the JSON fixture's explicit empty tuple. The corrected test asserts that
presence distinction and still compares complete fold records and memberships.
No expectation about memberships was relaxed. Initial mypy errors were resolved
with an explicit set[str] annotation and non-null domain filtering, without
ignores. Import ordering, line lengths and redundant parentheses were corrected.
The initial ordinary install could not fetch hatchling under restricted network
access; the authorized retry passed. Failed logs were retained, not overwritten.
No test was deleted or skipped. No unresolved S04 check failure is known.

Unverified: S02 ingestion integration; full Python 3.12/3.13 suites; other OSs;
CI; S14 Sphinx project/build; S16 standalone build, twine and clean-wheel matrix.
Pip built a wheel for installation, which does not complete the future release
gate. The foundation validator was not used as application QA. S05 and later
stages are unstarted. Human review and public release are not implied.
