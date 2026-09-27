# Sources and third-party components

The source register in `spec/21_sources.md` distinguishes background sources from
project choices. No external paper establishes this package's validity.

The implementation uses NumPy/pandas for arrays/tables, SciPy for descriptive
contingency association, scikit-learn for ordinary splitters, Pipeline and logistic
regression, Jinja2 for escaped templates and jsonschema for local contracts.
Dependencies retain their own licenses; no third-party implementation is vendored.

- [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)
  explains fitting boundaries and leakage.
- [Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html)
  composes controlled transformations; it cannot undo prior global fitting.
- [SciPy contingency association](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.association.html)
  provides the descriptive primitive, not a causal test.
- [Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/quickstart.html)
  describes the documentation tooling.

Publication and AI-disclosure policies must be checked for the intended venue at
submission time. No eligibility or acceptance is promised. No CITATION.cff or DOI
is supplied without verified author and release metadata.
