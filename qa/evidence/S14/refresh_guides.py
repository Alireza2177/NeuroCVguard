"""Remove historical stage-only wording; preserve the methodological guides."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPLACEMENTS = {
    "quickstart.md": [("demo/evaluation.private.json", "demo/participant.evaluation.private.json")],
    "cohort_checks.md": [
        (
            "strict use of these partial components by future planning/evaluation callers.",
            "strict use of these partial components by planning/evaluation callers.",
        ),
        (
            "The guard must be called by those future stages; those callers do not exist yet.",
            "The planner and evaluator call this guard before strict use.",
        ),
        (
            "small-cell display treatment and report rendering remain S08.",
            "small-cell display treatment and report rendering are implemented in reporting.",
        ),
    ],
    "association_diagnostics.md": [
        (
            "combined audit orchestration and report rendering belong to later stages.",
            "combined audit orchestration and report rendering use these same diagnostics.",
        ),
    ],
    "preprocessing_provenance.md": [
        (
            "It uses constructed `Cohort` objects because S02 ingestion remains unimplemented.",
            "It accepts validated `Cohort` objects returned by `load_cohort`.",
        ),
        (
            "comparison; CLI combination and HTML rendering are later stages.",
            "comparison; the CLI combines these checks and renders HTML.",
        ),
        ("The future evaluator must", "The controlled evaluator must"),
    ],
    "split_generation.md": [
        (
            "It writes nothing and fits no estimator. S02 ingestion is still unimplemented;\n"
            "pass a constructed, validated `Cohort`. The CLI still offers help/version only.",
            "It writes nothing and fits no estimator. Pass a validated `Cohort` from\n"
            "`load_cohort`; the CLI `split` command also writes operational artifacts.",
        ),
    ],
    "split_audits.md": [
        (
            "the representation future S02 integration must reuse; no second digest format",
            "the representation the cohort loader also uses; no second digest format",
        ),
        ("any future narrow", "the separate narrow"),
        ("not authorization or implemented model evaluation.", "not authorization or a model fit."),
        (
            "even if all split prerequisites pass. This does not implement S07 ledger checks\n"
            "or claim that a Pipeline can repair earlier fitting.",
            "even if all split prerequisites pass. Ledger checks are available separately\n"
            "through audit_cohort; a Pipeline cannot repair earlier fitting.",
        ),
        (
            "Rich table projection/rendering remains S08;",
            "Reporting supplies rich table projection/rendering;",
        ),
    ],
    "contracts.md": [
        (
            "remain loadable because their actual cohort audits belong to later stages.",
            "remain structurally loadable; audit_splits checks their actual cohort memberships.",
        ),
    ],
}
for name, pairs in REPLACEMENTS.items():
    path = ROOT / "docs" / name
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            raise ValueError((name, old))
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")

(ROOT / "README.md").write_text(
    """# NeuroCVguard

Research-only Python software for checking whether supplied cohort identities,
partitions and evaluation procedures match an intended generalization claim.
It reads local CSV/TSV/JSON, checks participant/transitive dependence and requested
domain separation, describes acquisition–target association, generates checked
splits and runs a controlled participant-level logistic baseline with optional
nested C selection. Offline HTML/JSON reports retain incomplete coverage and
limitations. No account, GPU or runtime internet connection is needed.

It does not process MRI images, provide clinical advice, authenticate upstream
preprocessing, prove causal confounding or certify a study as leakage-free.
Repeated visits alone are not leakage; inspect actual membership and objective.
Unknown upstream preprocessing remains unassessable even with a correct Pipeline.

## Install and try

From an authorized local source checkout, create a dedicated Python environment.
Use `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on Linux/macOS
after `python -m venv .venv`. With that interpreter selected:

```text
python -m pip install -e ".[dev,docs]"
python -m neurocvguard demo --out local_outputs/demo
```

Open `local_outputs/demo/report.html`. Inputs are fully synthetic, not patient
data. Choose a new output path or explicitly use `--overwrite`. Read warnings
beside coverage: association suggests reviewing acquisition imbalance, while
unknown preprocessing asks for evidence rather than a passing verdict.

**Private plans/evaluations are separate from projected reports.** Default
projection is not guaranteed anonymity; inspect artifacts before sharing.
The current local version is 0.1.0, not a published release or namespace claim.

## Documentation and development

- [Installation and troubleshooting](docs/installation.md)
- [Executable quickstart](docs/quickstart.md) and [synthetic tutorials](docs/synthetic_examples.md)
- [Inputs](docs/input_tables.md), [configuration](docs/configuration.md),
  [CLI](docs/cli.md) and [Python API](docs/api.rst)
- [Objectives/warning actions](docs/objectives.md), [evaluation](docs/evaluation.md),
  [report privacy](docs/reporting.md) and [limitations](docs/limitations.md)
- [Contributing/testing](CONTRIBUTING.md), [changelog](CHANGELOG.md),
  [security](SECURITY.md) and [release procedure](docs/release.md)

Build the full local site with
`python -m sphinx -W --keep-going -b html docs docs/_build/html` and open
`docs/_build/html/index.html`. Run
`python -m pytest -q --strict-markers --strict-config` for the test suite.
Actual stage evidence and unrun checks are recorded under `state/handoffs/`.
Windows local environments have been exercised; other platforms and dependency
minimums remain release checks. No remote CI pass is claimed.

## License, support and citation

BSD-3-Clause is proposed; [LICENSE](LICENSE) is not a finalized grant. Copyright,
maintainer identity, private security contact and public namespaces require owner
confirmation. Use the existing private owner channel for local support and share
only synthetic reproductions. No response-time commitment is claimed.
Citation metadata will be added only after verified authorship and release details;
no DOI or citation badge exists. [AI assistance](AI_ASSISTANCE.md) is recorded
honestly. Human walkthrough, external-user testing and acceptance remain pending.
""",
    encoding="utf-8",
)
