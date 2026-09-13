# S05 implementation review

Reviewed by the implementation AI on 2026-09-13. This is not an independent or
human review. S05 is the only newly implemented stage; human acceptance is pending.

Scientific behavior compared with spec chapters 06-08 and 20:

- The participant table is canonically ordered and has one target/component
  record per person. A splitter spy verifies equal inputs despite dramatically
  unequal visit counts; a direct standard-splitter oracle verifies assignments.
  Mixed-class families retain distinct participant targets. Property tests
  inspect literal protected-family intersections and complete observation coverage.
- Strict planning requires complete constant targets, two classes and known
  protected relationships. Incomplete relationship coverage stays unassessable,
  rather than being described as observed independence. Too few groups refuses
  the request before calling a splitter. No class, person or observation is removed.
- StratifiedGroupKFold receives exactly the requested fold count, shuffle=True
  and integer seed. It is called once. Class component counts are a necessary
  feasibility condition, not a guarantee of exact balance. Low counts are
  warnings; actual missing training classes reject the plan. An actual feasible
  low-component case retains a missing-test-class warning and all fold supports.
- LeaveOneGroupOut holds every represented site/phase once. Crossing participants
  or protected components, incomplete domains and fewer than two domains cause
  refusal. Tests cover both participant and family crossings without input mutation.
  Missing test classes are warnings while training remains class-complete.
- make_splits invokes the same independent audit_splits function as supplied
  plans. Injected observation contamination is refused with its scoped audit
  findings. Empty partitions and splitter infeasibility become PlanningError
  with separate blocked diagnostics, not a random-split fallback.
- Repeat/fold IDs, canonical observation memberships, cohort digest and generated
  plan hash match their contracts. Row permutations preserve plans/reports.
  NumPy global RNG state is unchanged for participant and domain schemes.
  Dependency versions are captured for the actual generation run.
- Unknown upstream preprocessing remains unassessable. No fitting, score,
  causal claim or global leakage-free conclusion was introduced. A successful
  split-level eligibility flag does not establish feature availability or an
  implemented evaluator. S05 refuses tune=true explicitly; S11 is not implemented.

Contract and ownership review:

The strict SplitPlan schema is unchanged. A nonconstructor, noncomparing runtime
field stores immutable generation_report, and an explicit dataclass serialization
metadata flag excludes it from operational JSON. Schema validation still rejects
that key in supplied JSON. Deserializing/replacing a plan clears its runtime
report, preventing copied history from being presented as observed generation.
The canonical plan hash is unaffected by attached runtime evidence.

PLANNING diagnostics use existing AuditReport/CheckResult contracts. Public
projection uses fixed rule wording and removes open evidence/raw keys. Private
reports retain requested seed/scheme/fold count, actual class support, and
successful plan binding details. PlanningError subclasses UnsupportedDesignError;
expected infeasibility is distinct from malformed configuration/input errors.
A narrowly scoped mypy override acknowledges sklearn's missing type metadata;
all NeuroCVguard code remains under strict checking. No runtime dependency was added.

Writer/privacy review:

Generation never writes files. Explicit SplitPlan.write creates canonical plan
JSON, outer TSV, a sensitivity notice and captured generation.private.json.
Imported plans without runtime evidence do not gain alleged historical versions.
All outputs are local and identity-bearing. Read-only/default public reports
still omit raw IDs, hashes and open evidence. Rejected diagnostics are separately
named, marked sensitive and cannot be mixed with usable-plan artifacts.

The writer validates all output names before writes, stages complete contents,
uses exclusive reservations by default and atomically replaces each file. Tests
verify collisions on every artifact, explicit overwrite, unrelated-file retention,
a competing writer after preflight, and storage failure during staging. This is
not a multi-file filesystem transaction: a failure during final replacement can
leave a partial bundle and raises an explicit error. No broader atomicity or
Windows ACL guarantee is claimed. Output symlinks are refused. Supplied nested
JSON is preserved and TSV stays outer-only.

Verification performed:

- 232 full-suite tests passed: 185 predecessor tests plus 47 S05 tests, with no
  failures, errors or skips. Ten acceptance cases map to 12 passing test nodes.
- Seven doctests passed separately. The documented synthetic generation/export
  example passed in the suite and in the isolated ordinary installation.
- Mypy passed all 17 source files; Ruff lint passed. Final formatting and
  preservation results are in commands.md and state/handoffs/S05.md.
- Ordinary Python 3.12 install, installed-code smoke outside the source tree and
  pip dependency consistency passed. Actual environments are recorded separately.

Retained failures and fixes: the first export run had two test-assumption errors.
The existing SplitPlan validator raises SplitValidationError (not its sibling
InputValidationError), and the existing config schema rejects an oversized seed
before make_splits is reached. Tests now assert those exact boundaries; input
validation was not weakened. Initial mypy import-untyped errors were resolved
only at the documented sklearn boundary. Import order, line lengths and a
one-character-too-long installed-probe output line were corrected. A restricted
pip install could not fetch hatchling; an authorized retry passed. Failed logs
remain intact. No test was deleted or skipped; no unresolved S05 check failure
is known.

Limits / NOT RUN: S02 ingestion integration; full Python 3.12/3.13 test matrices;
other operating systems; CI; S14 Sphinx build; S16 standalone build/twine/clean-wheel
release matrix. Pip's installation wheel is not the future release gate. The
foundation validator was not used as application QA. Only synthetic fixtures and
locally generated fictitious records were used; JUnit hostname is normalized to
LOCAL_HOST_REDACTED without changing names, outcomes, counts or timings.

Preservation is checked against 311 pre-edit files. Normative specifications,
contracts, fixtures, previous tests, prior evidence and handoffs remain unchanged.
All non-S05 project/QA rows retain their exact prior state. No public action or
S06 implementation was performed.
