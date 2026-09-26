# S13 implementation review

Implementing Codex agent review, 2026-09-26. No independent AI or human review is
claimed. Source instructions and the screenshot restriction are recorded in
`instruction_loading.md` and `screenshot-blocked.md`.

The generator draws six local NumPy Generator streams. Balanced participant
labels, participant-local session labels, site assignments and independent latent
vectors are explicit. Additive strength tests compare finite differences and
within-person constancy; association tests preserve labels/noise while changing
allocation. Global NumPy and Python RNG state are checked both for generation and
the complete default demo. Invalid parameters fail before allocation. No estimator
performance ordering is an invariant, and no seed was changed after observing a
score. In the retained repeated example the diagnostic accuracy is actually lower
than the participant-disjoint accuracy; the signed negative difference is retained.
The actual values and parameters are in executed/runs.json, not copied from a
conversation or used as independent expected metric oracles.

The default uses ordinary participant-disjoint split generation. Only the repeated
scenario explicitly invokes the S12 diagnostic option with row-random
StratifiedKFold. Existing prerequisites, fit boundaries, raw-row OOF pooling and
invalid-for-objective findings remain unchanged. Site-held-out evaluation uses
the existing domain planner and shows single-class test null metrics in example
03 while retaining all training classes. No family/domain/observation constraint
is waived. No cohort rows or labels are dropped or altered to force feasibility.

All tutorials generate local fictitious inputs and then exercise the normal
load_cohort/config/audit/plan/evaluation/report code. Example 05 proves keyed
alignment with reversed feature rows. Example 04 writes only a fictitious PCA
declaration; it never performs PCA or calls it observed history. Code, stdout,
metadata, README and reports label synthetic data. Public projection preserves
only one exact fixed notice; near-matching arbitrary text is still omitted, and
the notice never enables sensitive details. No schema or scientific contract was
weakened. Default output suppression and diagnostic warnings survive rerendering.

All generated files are staged before one existing atomic bundle write. Collision
and overwrite tests retain unrelated/prior files. Private manifests retain params,
versions, input digests and output checksums. Runtime manifests preserve actual
process argv; retained evidence redacts only machine-specific argv prefixes and
records that normalization. Other scientific artifacts remain checksum-identical.
The first smoke artifact predates prefixed-manifest correction and is explicitly
intermediate; the eight executed captures use the corrected implementation.

Python networking was denied in the full-workflow test fixture. The ordinary
installation separately exercises the module and console plus all five wheel
resources from a temporary cwd outside the source tree. Nothing downloads data,
reads patient tables, uses an account, deserializes estimators or runs dynamic user
code. Package force-inclusion covers the tutorial scripts; no public build/release
authorization is inferred.

Unsuccessful checks remain recorded: the initial unsupported provenance marker,
typing/import/line-length errors, and an evidence check that wrongly assumed
sys.orig_argv always points under the project rather than the base interpreter.
The marker was moved to the existing limitations contract; typing and style were
fixed; the evidence check now validates either normalized path prefix and forbids
the actual home prefix. No scientific assertion was relaxed or test skipped.

The preservation gate also caught a copied preparation-helper index that had
temporarily marked S12 in progress instead of S13. The helper now derives the
stage number, and the repair restores S12's exact captured baseline metadata and
assigns evidence to S13. The failing preservation result is retained, and the
unchanged assertion is rerun after repair. No human acceptance flag changed.

The genuine screenshot is BLOCKED by browser security. No alternative browser,
raw command, indirect serving workaround, generated mock image or fabricated
presentation review was attempted. HTML/JSON consistency checks are computational
evidence only. S13 cannot be READY_FOR_REVIEW until a genuine supplied screenshot
is verified or the user explicitly waives that specific artifact. The user
subsequently approved precisely that screenshot-only exception in ADR-S13-001.
No screenshot/visual review is claimed. S14 is untouched.
