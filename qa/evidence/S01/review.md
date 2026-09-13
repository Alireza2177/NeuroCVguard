# S01 implementation review

Reviewed by the implementation AI on 2026-09-13; not independent human review.

The delivered boundary is typed records, strict JSON/configuration validation,
offline packaged schemas and explicit serialization. No ingestion algorithm,
split generator, cohort audit, classifier fitting, metric calculation, HTML
renderer or later-stage CLI command was implemented.

The full suite passed 79 tests, including all 11 S00 bootstrap tests. A separate
doctest run passed 6 examples. All 11 S01 acceptance cases link to real passing
test nodes. Bundled structurally valid unknown-ID and overlap examples remain
loadable: actual cohort membership auditing belongs to later stages. No fixture,
schema or acceptance definition was rewritten to turn an invalid audit into a
valid one. No test was deleted or skipped to achieve a pass.

Reviewed scientific boundaries include objective-dependent split settings,
explicit roles, absence of role inference, declaration versus observed evidence,
unknown upstream preprocessing, null metrics with reasons, retained failed folds,
and class/coverage consistency. Records do not authenticate user assertions or
prove that a fit used the correct training subset. Actual auditing and fitting
remain required later work.

Reviewed privacy boundaries include immutable owned mappings, explicit sensitive
evaluation/plan/ledger exports, and public omission of IDs, hashes, paths and
open evidence/free text. S01 conservatively omits rich evidence rather than
attempting the future S08 rule-specific presentation. Public small-cell
suppression also hides linked fold/pooled metrics and dependent comparison
differences. Target class names remain visible as specified. This is not an
anonymity guarantee. No real participant data or external uploads were used.

Corrections are retained in the command history:

- Initial contract run: 2 failed, 29 passed. One assertion incorrectly expected
  unsorted memberships; spec/05 section 5.2 requires deterministic sorting. The
  assertion now compares the entire expected record after sorting only those
  membership lists and also verifies the input was not mutated. Other ordering
  remains unchanged. The other failure exposed InputValidationError being caught
  as ValueError; serialization now preserves the actionable projection error.
- Initial mypy failures were fixed through concrete annotations, local variable
  names and removal of a redundant cast; no type-check suppression was added.
- Lint/format failures were import order and line length; fixed in source/tests.
  A closeout check also detected mixed line endings after an evidence-runner
  docstring edit; formatting normalized the file and the retry passed.
- A type-stub installation failed under restricted network access. The authorized
  retry succeeded. Both attempts remain recorded. Stubs are development-only.

No unresolved S01 test failure is known. The latest passing records supersede
failed attempts without erasing them. Evidence JSON normalizes local paths;
JUnit hostnames are replaced with LOCAL_HOST_REDACTED without changing test
names, timings, outcomes or counts. Some early failure logs predate the explicit
UTF-8 capture correction and contain display mojibake; original outcomes remain.

Limitations: only Windows local checks ran. Python 3.11 ran the full suite;
Python 3.12 ran the ordinary installed-resource/configuration smoke check.
Full Python 3.12/3.13 and other-OS suites, strict Sphinx build (S14) and standalone
release build/twine/clean-wheel matrix (S16) are NOT RUN. Pip's ordinary install
built a wheel, but that is not a claim that the future release gate passed.
The pristine-foundation validator was NOT RUN as application QA.

No normative files or S00 historical evidence are intended to change. Live
metadata, README, assistance record, S01 status and QA tracking are updated
truthfully. Human acceptance is pending and work stops at S01.
