"""Join reversed synthetic feature rows by scan_key with explicit role/feature names.

Run: python examples/05_explicit_feature_join.py --out local_outputs/example-05
The installed workflow writes local TSVs and uses load_cohort's keyed join.
No hidden notebook state, external dataset or row-order alignment is used.
"""

from neurocvguard.demo import example_main

if __name__ == "__main__":
    raise SystemExit(example_main(5))
