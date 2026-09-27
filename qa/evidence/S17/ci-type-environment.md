# Hosted CI type-check environment correction

Run 36299183458, Linux Python 3.12 job 108563541689 passed the full source suite,
lint and format, then mypy exited 2 before checking application code:

```text
numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater [syntax]
Found 1 error in 1 file (errors prevented further checking)
```

The project deliberately targets Python 3.11 in mypy. The Python 3.12 environment
resolved NumPy stubs using Python 3.12 type-statement syntax. Move the unchanged
mypy command to the existing Linux Python 3.11 job, whose dependency stubs must
support 3.11. Retain the target, all type assertions, all six platform source
suites and the strict documentation check on 3.12. No package/runtime bytes,
dependency requirements or scientific tests change. Preserve this failed run;
a fresh hosted run will verify the corrected workflow before release.
