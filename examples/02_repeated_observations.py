"""Compare row-random diagnostic and participant-disjoint synthetic evaluations.

Run: python examples/02_repeated_observations.py --out local_outputs/example-02
The row-random score is invalid for unseen-participant generalization.
No universal ordering or causal leakage amount is claimed.
"""

from neurocvguard.demo import example_main

if __name__ == "__main__":
    raise SystemExit(example_main(2))
