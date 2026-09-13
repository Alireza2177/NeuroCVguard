# S03 implementation review

Reviewed by the implementation AI on 2026-09-13. This is not independent or human
review. Human acceptance remains pending for S00, S01 and S03.

S03.A/B/C are implemented as pure library checks over S01 Cohort records. The
stage selection deliberately follows the user's S03-only instruction; the normal
S02 predecessor is unimplemented. No S02 ingestion, keyed join, cohort digest
construction or S04 split auditor was added. Fixture loading in tests is an
explicit adapter for known synthetic tables, not a public application loader.

Scientific checks reviewed and exercised:

- 18 participants/36 observations; target counts at both units; participant-local
  session values; multiple observations in one person/session pair retained.
- Repeats are information, with no split violation. The clean fixture's supplied
  participant-disjoint plan is checked independently in the known-answer test.
- Target changes are described as a meaningful longitudinal possibility and
  block the constant-target prerequisite without relabeling or removing people.
- Protected components use union–find, distinct relationship namespaces,
  transitive links including multiple values within a person, deterministic
  sorted memberships and singletons. A separate graph traversal is the property
  test oracle. Participant identity survives site changes and row permutations.
- Missing/malformed relationship values add no links. Incomplete relationships
  expose a strict-use guard that raises; no unknown values are treated as verified
  independent groups. Mapped session labels are rejected as global relationship
  keys. No physical identity is inferred from features or source namespaces.
- Exact equality canonicalizes signed zero and matching missing positions,
  skips all-missing vectors and preserves near-but-unequal finite values. A
  mocked constant primary hash cannot manufacture equality, including a 3,000-row
  distinct-vector case. The production implementation groups complete tuple keys
  rather than scanning all row pairs. No benchmark performance claim is made.
- Equality remains warning/heuristic evidence. The existing public projection
  now uses fixed S03 wording instead of describing heuristic matches as generic
  violations. Evidence/identifiers remain omitted publicly. Internal unsuppressed
  counts are separate from later presentation. No causal or clinical claim is made.

Ownership/privacy: returned detail uses immutable tuples/frozen records and
read-only maps. Source/returned pandas tables remain caller-owned copies at the
existing Cohort boundary. Raw inventories, IDs, component hashes and equality
memberships remain sensitive local data. No public raw-record serializer, output
writer, telemetry or dataset download was added. Errors identify roles/counts
without raw participant values. JUnit hostnames are normalized to
LOCAL_HOST_REDACTED; test names, outcomes, timings and counts are unchanged.

Actual verification: 130 full-suite tests passed (79 predecessor tests plus 51
S03 tests); no failures, errors or skips. Seven doctests passed separately. The
Markdown example passed within the suite and again after formatting. Mypy passed
13 source files; Ruff and formatting passed. The ordinary Python 3.12 installation
and isolated installed-code smoke passed; its dependency check passed.

Retained intermediate failures: two mypy overload errors around pandas scalar
missingness were fixed with a shared runtime scalar guard and a localized typing
cast at the pandas boundary. Import-order/long-line lint failures were corrected.
The final-format attempt found the new Markdown example needed formatting; the
document was formatted and the example and formatter passed again. The initial
ordinary installation could not obtain hatchling with restricted network access;
an authorized retry succeeded. No test ever failed in this S03 run, and no test
was removed, weakened or skipped. There are no known unresolved S03 test failures.

Unverified boundaries: S02 ingestion integration; full Python 3.12/3.13 suites;
other operating systems; S14 Sphinx project/build; S16 standalone release build,
twine and clean-wheel matrix; CI. Pip built a wheel for ordinary installation,
which is not a claim that the future S16 release gate passed. The foundation
validator was not used as application QA. Future planners/evaluators must invoke
the prerequisite guards and run their own broader design checks.

Preservation is checked against the 213-file baseline, with exact non-S03 QA
rows/statuses retained. Only expected live metadata, public wording and tracking
files may differ. Specification, contracts, fixtures, prior evidence and handoffs
remain unchanged. Work stops at S03; no S04 work or public action is authorized.
