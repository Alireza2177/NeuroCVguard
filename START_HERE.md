# Start here — NeuroCVguard foundation

This is the **Step 0 implementation foundation**, not the finished software. It tells Codex what to build, which scientific claims are allowed, how to prove behavior, and where human release decisions are required.

## The first action

Extract the archive into a new local project directory, or copy its contents into the intended repository without replacing unrelated files. Keep AGENTS.md at the repository root. Open that directory in your Codex environment and submit this prompt:

```text
Read AGENTS.md, START_HERE.md and state/PROJECT_STATUS.json.
Then read prompts/S00_bootstrap.md and every specification file it lists.
Implement stage S00 only. Preserve unrelated files. Follow the scientific
scope and acceptance requirements. Run the checks you can actually run,
record exact commands and results, and write state/handoffs/S00.md.
Do not implement later stages, publish anything, invent metadata or claim
that unrun tests passed. Stop with S00 ready for human review, or state
precisely which requirement is blocked.
```

Do not ask Codex to “build all of this in one go.” The stage prompts are designed to limit context drift, expose mistakes early and make progress reviewable. They are not a guarantee that generated code is correct.

## Continuing

After reviewing the stage's actual diff and test evidence, give an explicit acceptance instruction and select the next prompt. For example:

```text
I have reviewed and accept S00. Record my acceptance in the project status.
Read prompts/S01_models_contracts.md and its listed specifications.
Implement S01 only, run its required checks, write its handoff, and stop.
```

Only say you have reviewed something when you actually have. A separate agent review can help identify defects but is not a substitute for human scientific responsibility. When a session loses context, use prompts/RESUME.md. When a stage is doubtful, use prompts/REVIEW.md rather than asking for more features.

## Where each kind of information lives

| File or directory | Purpose |
|---|---|
| `NeuroCVguard_MASTER_SPEC.md` | Complete assembled reading/reference document |
| `NeuroCVguard_READABLE.html` | Offline browser-readable edition with navigation |
| `AGENTS.md` | Short always-read repository instructions |
| `spec/` | Normative scientific, engineering, usability and release chapters |
| `prompts/` | One executable instruction set per stage plus review/resume prompts |
| `contracts/` | Strict, standalone JSON schemas for external contracts |
| `fixtures/` | Synthetic known-answer inputs and deliberately invalid examples |
| `qa/` | Requirement, rule and acceptance-case registers; no invented test results |
| `state/` | Implementation status, stage graph and decision/handoff records |
| `templates/` | Review, handoff, decision and release records to fill with actual evidence |
| `tools/validate_foundation.py` | Checks foundation consistency, not future application correctness |
| `tools/build_master.py` | Reassembles master/reader from the split source documents |

The source of truth for future edits is spec/ plus the schemas, prompts and registers, not hand-edited copies of the generated master. Regenerate the master after approved foundation changes. Keep changes to scientific behavior in an explicit decision record.

## What the finished first release will do

Read authorized local cohort/feature tables; inspect participant/dependency and requested domain separation; describe acquisition–target association; show unknown preprocessing history honestly; generate checked splits; run a controlled participant-level classification baseline; and write useful local reports. It will have tested installation, API/CLI, documentation, synthetic examples and a reviewed release process.

It will not process MRI images, guarantee absence of all leakage, infer causal bias, certify clinical use or promise a paper. The baseline intentionally does not support every modeling task. Existing scikit-learn and SciPy components are reused rather than replaced.

## Validation of this foundation

A local check of schemas, fixtures, stage references and document integrity can be run with:

```bash
python -m pip install jsonschema
python tools/validate_foundation.py
```

The check must report its scope explicitly. Passing it means the **foundation artifacts are consistent under those checks**. It does not mean NeuroCVguard has been coded, its tests have passed, or it is ready to publish.

The default command above validates the original, unimplemented foundation and
therefore rejects a repository whose application stages have progressed. During
implementation, use `python tools/validate_foundation.py --mode artifacts` for
the shared document/schema/fixture checks. This mode explicitly lists the three
snapshot-only checks outside its scope; it does not assess application tests,
human acceptance or release readiness. Both modes print results without writing
a record by default. Add `--output PATH` to save a new JSON record; existing paths
are refused so historical evidence is preserved.

## Release checkpoint

S00–S16 prepare and validate locally. S17 is the explicit public-release gate. Repository pushes, package publishing, public visibility changes and DOI registration require actual owner authorization. The foundation contains no credentials and assumes no repository/package name has been reserved.
