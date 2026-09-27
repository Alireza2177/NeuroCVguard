# S16 local release-candidate dossier

Version: 0.1.0. Evidence date: 2026-09-27. Local candidate: READY_FOR_REVIEW.
Human acceptance and public release: pending; publication is not authorized.
Selected base commit: `901da5736add73b615668e57ccfa259c5fa1b72e`.
S16 changes remain uncommitted; this is not a tagged release. The recorded archive
and payload hashes identify the tested candidate without inventing a release commit.
The user's explicit S16 request authorizes progression from completed S15 outputs;
it does not change any stage's human-acceptance flag. S17 remains NOT_STARTED.

## Distribution identity

Artifacts are local, under `dist/s16/`. Isolated build used hatchling 1.32.4 and
built the wheel from the sdist. Both passed `twine check --strict`. Exact archive
allowlists and byte comparisons passed for all 53 runtime payloads: 39 package
Python files, six schemas, HTML/CSS, `py.typed` and five executable examples.
The source archive also contains the root README, proposed license, pyproject,
`.gitignore` and generated metadata. No tests, private outputs or internal history
are distributed. The included license notice remains pending owner confirmation.

| File | Bytes | SHA256 |
|---|---:|---|
| neurocvguard-0.1.0-py3-none-any.whl | 131961 | `2997e8d1ef5dd09d8a66aead05e165960a08b040b7949436fa02c8945db45386` |
| neurocvguard-0.1.0.tar.gz | 102707 | `6325ca9863b2a59294c837acdbdcbe780352cf441cb97cd07e284c44d4c15deb` |

Full members, requirements and individual payload hashes are in
`qa/evidence/S16/distributions.json`. The candidate input hashes and preservation
check are in `qa/evidence/S16/preservation.json`. No runtime source, contract or
scientific behavior changed in S16. Packaging now uses anchored sdist include paths
and six tested direct-dependency lower bounds.

## Actual execution matrix

| Environment | Installation / scope | Actual result |
|---|---|---|
| Linux WSL2, Python 3.11.16 | Isolated editable source snapshot, full existing suite | 712 passed; then 9 new archive tests passed separately |
| Linux WSL2, Python 3.12.14 | Same scope, independent interpreter/environment | 712 passed; then 9 archive tests passed separately |
| Linux WSL2, Python 3.13.15 | Same scope, independent interpreter/environment | 712 passed; then 9 archive tests passed separately |
| Windows build 26200, Python 3.12.3 | Installed initial wheel, copied runtime tests outside source | First run: 672 passed, 6 failed, 1 deselected; corrected bundle: all 6 failed cases passed |
| Windows build 26200, Python 3.11.7 | Installed wheel with exact direct-dependency floor | First run: 672 passed, 7 failed; corrected catalog: 6 passed; remaining editable-only test is inapplicable to wheel scope |
| Windows, Python 3.12.3 | Fresh final wheel, runtime dependencies only | Import, real console version/help, dependency consistency, all assets and offline default demo passed |
| Linux WSL2, Python 3.12.14 | Fresh final wheel, runtime dependencies only | Same final-wheel checks passed |
| Windows, Python 3.11.7 | Final wheel installed into tested floor environment | Dependency consistency, all assets and offline default demo passed |
| macOS, Python 3.12 | No available host | NOT RUN |
| Hosted CI | Local matrix only | NOT RUN |

Linux was x86_64, glibc 2.35, kernel
5.15.167.4-microsoft-standard-WSL2. This does not establish support for every Linux
distribution. Python versions beyond the tested matrix remain unverified.
The Linux full suites ran before final packaging metadata/docs edits; all runtime
bytes are unchanged. The nine archive tests ran after their addition. Each Linux
environment therefore covered 721 unique tests across two commands, not one
721-test full-suite command.

The six Windows failures were a copied-test-bundle omission of
`qa/rule_catalog.json`, corrected without changing application code or assertions.
All six were rerun successfully in both environments. The minimum run's seventh
failure was an editable-install-only bootstrap check accidentally selected by an
incorrect deselection node. That check passes in all three Linux source suites;
it is deliberately replaced in wheel scope by a stronger non-editable install
proof. Both Windows runtime environments have 678 unique passing runtime cases
across their initial and corrective runs. The 24 documentation cases and nine
foundation-validator cases were outside wheel-runtime scope and passed in the
Linux full suites. Every original failed command and output is retained.

The initial wheel's 53 runtime payloads equal the final wheel/source payloads;
only packaging metadata/content selection changed. Final probes independently
check all 53 installed bytes against the final wheel hash. They run outside the
repository with isolated Python, assert a non-editable site-packages location and
block repository file access plus network socket events through an audit hook.
The sole socket-event exception is `socket.gethostname`, a local hostname lookup.
Demo execution completes; the audit report correctly remains partial because
upstream preprocessing is unassessable. This is not a leakage-free verdict.

## Dependency evidence and quality gates

The Python 3.11 floor uses NumPy 1.26.4, pandas 2.2.3, SciPy 1.13.1,
scikit-learn 1.5.2, Jinja2 3.1.6 and jsonschema 4.23.0. Exact pins are in
`requirements/minimum-py311.txt`. Transitive versions were resolved and recorded,
not claimed to be their minimum versions. These conservative tested direct bounds
are not a claim that earlier versions cannot work. Library requirements use lower
bounds without invented upper bounds. Newer Python may resolve newer dependencies.
Fresh final-wheel Python 3.12 checks used NumPy 2.5.3, pandas 3.0.6,
SciPy 1.18.1, scikit-learn 1.9.1, Jinja2 3.1.6 and jsonschema 4.26.0.

S16 records include strict metadata, exact-content checks, nine negative/positive
archive tests, Ruff lint/format, strict mypy and the warnings-as-errors Sphinx
build. Exact argument vectors, exit codes, environment and output are indexed in
`qa/evidence/S16/commands.md`. The full platform test counts are mechanically
reconciled from JUnit in `qa/evidence/S16/platform-matrix.json`.

S15 coverage and mutation evidence is retained, not rerun or relabeled as S16:
96.3308% package line coverage, 90.0729% branch coverage, every designated core
module at least 95% line coverage, and ten caught mutants with restored controls.
See `qa/evidence/S15/coverage-gate.json` and `mutation-results.json`. S16 verifies
runtime bytes are unchanged from the entry revision. S15's approved dependency
first-import Python RNG exception remains in force; NumPy and seeded scientific
behavior are not relaxed. No result-changing defect was established by the
bounded S16 review or executed checks. Human scientific acceptance remains pending.

## Privacy and unresolved release gates

The location-only scan reviewed 1,104 tracked paths: 475 matches, comprising
331 known synthetic participant labels, 132 historical/adversarial path locations
and 12 third-party-license/synthetic email-like locations. No credential-shaped
matches or files above 1 MB were found. This is not exhaustive secret detection
or proof of anonymity. Runtime, examples and root distribution metadata had none
of those matches. Exact distribution allowlists exclude the internal evidence,
fixtures, tests and generated foundation readers where matches occurred.

Historical evidence retains local machine paths. The entire repository and its
history are not cleared for public release by the package scan. Human review must
confirm the intended public surface and metadata before publication. Owner name,
copyright/license adoption, security contact, repository and package ownership,
real citation metadata, stage acceptance, maintainer walkthrough and independent
user exercise remain pending. No identity, review, DOI or authorization is invented.
macOS/hosted checks remain unexecuted. See the accompanying S16 checklist.

No public push, tag, upload, DOI registration or visibility change occurred.
Final public-release authorization is false. S17 requires a new explicit request.
