# S15 independent AI review and resolutions

Reviewer: separate Codex agent `s15_review`, fresh context, explicitly authorized
by the user. Read-only review; no agent edits or full-suite run. Human scientific
review and stage acceptance remain pending. Parent implementation review is
separate. Instruction sources loaded by reviewer: AGENTS/START_HERE/status,
S15 prompt and its listed chapters, acceptance cases/rule catalog, relevant
schemas and the S14 handoff. All prior human-accepted flags remain false.

## Findings

1. P2 local-only boundary: config initially lacked a UNC guard; split writers
   probed existing output files before locality validation; mixed Windows slash
   forms bypassed raw-prefix guards elsewhere. Mocked filesystem probes established
   this without contacting any host. Fixed with one pure normalized-spelling
   classifier in _paths.py and early checks in config, tables, plan/ledger/private
   evaluation/CLI JSON loading, demos and report/split writes. No network path is
   opened by a reproduction. The reviewer independently confirmed 12 rejections
   and zero filesystem probes, and 43 focused tests passed. The 40-case regression
   matrix was improved to use a literal sentinel as its independent probe oracle.
2. P2 public alias collision: valid classes @private and Target 001 both became
   Target 001 and violated the report schema's uniqueness rule. A valid private
   record could fail public export. Fixed by reserving every retained semantic
   class label before assigning aliases, using the same mapping algorithm for
   class order, MetricSet classes and comparison context/positive class. Tests
   cover defined metrics, private preservation and re-projection idempotence.
   The reviewer inspected the fix and confirmed consistent collision handling.
3. First-import RNG side effect: reproduced independently and in cold-rng.json.
   scikit-learn 1.9.1 imports Rich 15.0.0 progress-bar style identifiers via Python
   getrandbits(24). NumPy and seeded splits are unchanged; subsequent calls
   preserve both RNGs. The user explicitly approved only this first-import
   limitation in ADR-S15-001. It remains disclosed, not called a passed invariant.
   No global-state save/restore or dependency patch was introduced.

No additional result-changing defect was established in the inspected participant
and transitive partitions, keyed joins, outer/inner fitting, weights, class/null
metrics, failed-fold pooling or linked privacy suppression. This is bounded AI
review, not proof that all defects are absent.

## Security and resources

security-inventory.json records 359 runtime import statements, installed versions,
dependency license metadata/texts and hashes. The AST inventory found no listed
unsafe executable/deserialization/network calls. Source inspection confirms
allowlisted CSV/TSV/JSON, duplicate-key/nonfinite guards, packaged-only schemas,
no user code execution, escaped static templates and atomic named outputs.
Socket interception covers init/validate/audit/split/evaluate/compare/report/demo,
including DNS, connect and connect_ex. Hostile CSV instructions stay inert.
The independent path oracle additionally protects against OS network filesystem
access, which Python socket interception alone would not catch.

Dependency review: NumPy/pandas/SciPy/sklearn retain BSD-family notices (NumPy
also bundles separately listed permissive components); Jinja2 retains its
redistribution notice; jsonschema/MyST/pytest MIT notices; Sphinx BSD-2-Clause;
Hypothesis MPL-2.0 is a development dependency. Complete installed notices are
retained for review; no dependency implementation was copied into the package.
No production dependency added, no executable GitHub workflow or publication
secret introduced. This is not a current vulnerability-database audit or legal
certification. Project license/contact/author ownership remains unconfirmed.

Benchmarks use deterministic synthetic inputs and two fresh processes per case.
Actual OS peak working set includes interpreter/imports/input construction;
operation time excludes setup. Inventory at 10k/100k, full audit and split at 10k,
and 240-row/12-feature baseline are in benchmark-results.json. The host also ran
verification work, so timings are descriptive measurements, not isolated speed
guarantees. Inventory grew about 12–13x for 10x rows, inconsistent with a quadratic
trend in these measurements. Source uses per-field passes, union-find and hash
buckets/exact equality rather than all-pairs group/duplicate scans. Early limits
are verified before avoidable feature allocation/copy, not claimed as process
memory caps. No silent data truncation or optimization changed scientific rules.

## Fault detection and failures retained

All ten required temporary faults were detected (pytest exit 1), then restored
copies passed (exit 0). Exact replacements, tests, logs and hashes are retained
in mutation-results.json. Mutations ran only in owned temporary source copies;
the active production files were never corrupted.

Initial new property tests mistakenly compared normalized loaded dtypes with
raw pandas StringDtype; corrected to test caller-data and loaded-data preservation
separately without relaxing equality. First-import RNG is disclosed separately.
Early path tests had guessed loader names and missing ledger context, then a
global probe mock disrupted pytest internals; corrected names/context and guarded
only the independently named remote sentinel. A fixture initially had null metrics;
the collision test now uses a defined synthetic contract metric record. An existing
output-message assertion caught a wording regression; production wording was fixed,
not the assertion. Security recorder/output filename collision left the generated
inventory intact; security-record-check.json verifies the retained result.
Failed commands remain recorded. No existing test was removed or weakened.

## Coverage instrumentation correction

The first complete run passed 644 tests, but subprocess coverage was absent and
source edits during that exploratory run made its line map unsuitable as final
coverage evidence. Coverage.py's supported subprocess patch now measures actual
CLI and tutorial subprocesses, without source exclusions.

The first expanded run had 702 passing tests and one import-probe failure:
Coverage's own atexit database write violated the probe's strict write prohibition.
Only that child's instrumentation environment is now removed; all original audit
hooks and assertions remain. The corrective instrumented test passed. Other
subprocesses continue to measure imports. No production behavior was changed.

That corrective run used Coverage's default file prefix, whose erase operation
also removed the earlier shard data. The failed combination attempt is retained
in coverage-gate-check.json. The entire final suite is therefore rerun with each
shard's coverage data in its own ignored directory. Original run logs and XML
remain intact; only the new verified-* runs are final suite/coverage evidence.

Final result: all 703 unique tests passed in four disjoint groups, without skips
or expected failures. Combined coverage is 96.33% lines and 90.07% branches;
every checked core module is at least 95% line-covered. The unmodified 90/85/95
thresholds pass without added exclusions. All 644 exploratory baseline cases
remain in the final suite. preservation.json records the file and stage audit.

An additional standalone foundation-validator attempt failed on Windows schema
key separators before writing a record. Baseline hashes confirm its script and
manifest were unchanged on entry. That script also requires all stages unstarted
and cases unrun; it validates the original frozen foundation, not an implemented
application. It is retained with the failure disclosed, not weakened to produce
a pass. See foundation-record-consistency.json and foundation-baseline-scope.json.

Follow-up: the user's request for the most defensible approach authorized the
bounded repair in ADR-S15-002. The old attempt above is historical evidence.
The repaired validator now uses portable schema keys and explicit artifact scope;
all 124 shared checks pass. Default snapshot mode retains its three assertions
and correctly rejects progressed state. Existing output is never overwritten.
Nine focused regression tests pass, including deliberate fixture corruption and
successful original-snapshot conditions. A test-discovered unknown-ID crash was
fixed without removing the failing check. This follow-up was reviewed by the
implementing agent only. Scientific code, human flags and later stages are unchanged.
