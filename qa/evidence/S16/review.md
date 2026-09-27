# S16 packaging and release-readiness review

Implementing-agent review only. The user explicitly selected S16 after S14/S15
completion; that authorizes local S16 work, not human acceptance or publication.
Entry tree was clean at 901da5736add73b615668e57ccfa259c5fa1b72e. All human acceptance
flags were false; no accepted handoff exists. The latest completed handoff is S15.

Instruction sources opened: AGENTS.md, START_HERE.md, PROJECT_STATUS.json,
prompts/S16_release_candidate.md (S16 prompt), S15 handoff, spec chapters 00, 03,
05, 13, 14, 16, 17, 18 and 20, all S16 acceptance cases/requirement, rule catalog,
templates/RELEASE_CHECKLIST.md, pyproject.toml, release/installation guidance and
relevant CLI/demo/schema/evaluation/test code. Actual prompt filename is also
recorded in the stage plan; no generated master replaces the normative chapters.

## Findings and corrections

The initial sdist included fixtures/README.md because an unanchored README pattern
matched nested files. Anchored package include paths restrict the archive to the
intended source, examples and root metadata. Both archive payloads are compared
byte-for-byte to selected source, not just checked for a few expected filenames.
An exact allowlist rejects missing/extra/duplicate archive entries. New tests
include missing schema/CSS, altered bytes/version, private files, traversal names
and accidental runtime-resource inclusion.

The first wheel probe was launched with repository cwd. Subsequent diagnosis
showed its network guard also rejected socket.gethostname, a local information
lookup used by dependencies. The corrected probe runs outside the repository
and permits only that non-network event; sockets, DNS and connections are still
blocked. It verifies installed location, no editable metadata/source path,
packaged assets, and a real default demo. The first successful demo then exposed
a probe assertion mistake: demo execution completes while its audit report is
partial because metadata/upstream history remain unassessable. The corrected
oracle checks both statuses and the explicit unknown-provenance finding. No
application behavior or scientific assertion was changed to satisfy the probe.

WSL /tmp did not persist between short sessions. Interpreter/source setup was
repeated under an owned /var/tmp directory. Initial setup failures remain recorded.
Downloaded interpreters and dependencies are test setup, not a runtime network
dependency. No system Python or unrelated environment was replaced.

## Privacy/security review

privacy-scan-data.json scans 1,104 tracked paths and records only match locations,
not matched values. No credential-shaped hits or files above 1 MB were found.
The 475 review locations comprise 331 participant-shaped labels in known synthetic
fixtures/tests and their generated specification copies, 132 absolute-path
locations in historical local evidence or adversarial tests, and 12 email-like
locations in third-party license notices or synthetic tests. Every hit lies in
qa/evidence, tests, fixtures or generated foundation readers; none lies in runtime
source, root distribution metadata or examples. This is bounded pattern review,
not proof of anonymity or a complete secret scan.

Historical evidence retains local paths. The whole development repository is not
automatically cleared for public release; archive allowlists exclude that internal
history. A public repository/history review remains an S17 owner decision. Built
distributions include the proposed license notice but no finalized ownership or
invented author/security contact/DOI. No release credentials were read, no
publication workflow enabled, and no push, tag, upload or DOI request was made.

## Scientific scope

S15's separate AI review findings are resolved in the unchanged runtime sources.
The approved Rich/scikit-learn first-import RNG exception remains disclosed.
No new result-changing defect was established in S16. Platform runs,
dependency verification and final archive results are separately recorded; failed
or unavailable checks must not be called passed. Human scientific review and the
maintainer/external-user walkthrough remain pending.

## Final execution review

Each Linux source suite passed 712 tests, followed by nine new archive cases.
Windows wheel suites exposed an omitted rule catalog in the copied test bundle:
six failures in each environment passed on exact corrective reruns. The minimum
run also accidentally selected an editable-only bootstrap case; that check passes
in all Linux source suites and is inapplicable to wheel-only scope. The final
non-editable probes separately prove installed provenance. No failing scientific
test was deleted or weakened. Initial failed records are preserved.

Final fresh Windows/Linux probes and the minimum-dependency final-wheel probe
match all 53 installed payloads to the final wheel hash. Both archives have exact
allowlists and source byte equality. The first lint run found three long lines
and a Python-version alias warning in the Python 3.10 WSL bootstrap helper; lines
were wrapped and the one alias warning was narrowly annotated for compatibility.
No runtime source changed. macOS, hosted CI and human release gates remain pending.
