"""Map generated cohort TSV, audit and create participant-disjoint CV; open report.html.

Run: python examples/01_cohort_audit.py --out local_outputs/example-01
All inputs are created locally by the installed package; no patient data.
"""

from neurocvguard.demo import example_main

if __name__ == "__main__":
    raise SystemExit(example_main(1))
