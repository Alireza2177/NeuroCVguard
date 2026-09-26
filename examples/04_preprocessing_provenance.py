"""Compare unknown preprocessing with a fictitious global-PCA declaration.

Run: python examples/04_preprocessing_provenance.py --out local_outputs/example-04
Inspect report.html and unknown.report.html. No PCA actually runs; a declaration
cannot authenticate historical execution, and a Pipeline cannot repair it.
"""

from neurocvguard.demo import example_main

if __name__ == "__main__":
    raise SystemExit(example_main(4))
