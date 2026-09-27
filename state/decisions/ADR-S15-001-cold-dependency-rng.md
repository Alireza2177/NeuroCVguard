# ADR-S15-001 — Cold dependency initialization and Python global RNG

Status: ACCEPTED by explicit user decision, 2026-09-26 UTC.

The user answered: “Approve documented first-import exception”. This approves
only the first-import limitation below, not human stage acceptance, publication
or any later stage.

## Counterexample and scope

Spec 16.2 names no global-RNG mutation as a property invariant. In the exercised
Windows/Python 3.11 environment, the first public make_splits call lazily imports
scikit-learn 1.9.1. Its callback progress-bar module imports rich.style, whose
module initialization calls Python random.getrandbits(24) for style identifiers.
Thus Python's process-global RNG changes on the first call. NumPy's global RNG
does not change. A second call changes neither RNG, and plans are identical.
qa/evidence/S15/cold_rng.py is the concrete fresh-process reproducer; its command
record retains the actual stack/version evidence. The independent AI reviewer
reproduced this separately.

The scientific algorithms use explicit seeds/local generators; no seed is chosen
by score. No split, probability or metric defect was found from this import effect.
Post-import property tests still require both global RNGs to remain unchanged.
Those tests cannot be described as a passing cold-public-call invariant.

## Approved decision

Accept a narrowly documented dependency-initialization limitation for this local
stage: third-party first import may consume Python's global RNG. Retain the
counterexample and dependency versions, disclose it in installation/limitations,
and keep all algorithmic NumPy/Python RNG, deterministic plan and fit-boundary
tests unchanged. Do not claim the literal cold-call condition passed.

No process-global RNG save/restore or monkeypatch will be added to production:
it can overwrite concurrent callers' random draws. No third-party installed source
will be silently patched. Dependency compatibility and release readiness remain
separate S16 work. Human stage acceptance is not inferred.

Alternative: leave S15 blocked on the cold-call invariant until a reviewed
dependency change eliminates it. No change of dependency or contract is made
without an explicit decision.
