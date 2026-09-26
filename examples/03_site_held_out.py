"""Hold sites out with explicit class-associated domains; retain undefined fold metrics.

Run: python examples/03_site_held_out.py --out local_outputs/example-03
Association=1 is an explicit pedagogical mechanism, not a selected favorable seed.
Site/participant objectives differ; these tabular data are entirely fictitious.
"""

from neurocvguard.demo import example_main

if __name__ == "__main__":
    raise SystemExit(example_main(3))
