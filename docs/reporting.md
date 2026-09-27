# Offline report API

S08 renders already computed records. It does not load cohort files, run model
evaluation, or implement the S09 command-line report workflow.

This synthetic example runs in a temporary directory and is exercised by tests
and the ordinary installed-package check:

```python
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from neurocvguard import audit_cohort, write_report
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.models import AuditReport, Cohort
from neurocvguard.reporting import render_report, write_findings_csv

data = pd.DataFrame(
    {
        "observation_id": ["synthetic-o1", "synthetic-o2"],
        "subject_id": ["synthetic-p1", "synthetic-p2"],
        "diagnosis": ["class A", "class B"],
    }
)
config = AuditConfig(columns=ColumnMap(session=None, site=None, phase=None))
cohort = Cohort(data, None, config.columns, tuple(data.observation_id))
result = audit_cohort(cohort, config=config)
with TemporaryDirectory(prefix="neurocvguard-report-example-") as directory:
    paths = write_report(result, output_dir=Path(directory) / "public")
    public = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert public == result.to_dict()
    html = paths["html"].read_text(encoding="utf-8")
    assert "Incomplete assessment coverage" in html
    assert "synthetic-p1" not in html
    assert render_report(AuditReport.from_dict(public)) == html
    csv_path = write_findings_csv(result, path=Path(directory) / "findings.csv")
    assert csv_path.is_file()
```

`write_report(result, *, output_dir, sensitive_details=False, overwrite=False)`
accepts `AuditReport`, `EvaluationResult` or `ComparisonResult` and returns `json`,
`html` and `manifest` paths. `render_report` returns the same HTML without writing.
The HTML opens directly as a local file, with inline packaged CSS, contents links,
table captions and print styles. It contains no scripts, external fonts or assets.
Undefined values and failed folds remain visible with their supplied reasons.
No statistic, fold aggregation or participant grouping runs during rendering.

The JSON payload is exactly the shared `result.to_dict(...)` projection. Audit
and evaluation reports retain the existing versioned audit-report envelope.
The established `ComparisonResult` contract is a standalone comparison-summary;
the versioned `report.manifest.json` identifies this schema without adding
unsupported fields or inventing a cohort inventory. Comparison records cannot
restore absent audit coverage. All three files are part of the report bundle.

## Privacy

Default output omits raw IDs, paths, per-person predictions, operational hashes
and open user text. Site, phase and other acquisition labels use deterministic
aliases within that report, without a reverse map. Table target labels are also
aliased conservatively. Semantic metric class labels remain available; path-like,
email-like and control-bearing class labels are replaced with target aliases.
Aggregate counts and target names can still be sensitive: this is not formal
anonymization or a compliance guarantee.

The default small-cell threshold is five. A table is displayed only when every
cell meets the threshold; zeros also conservatively suppress the whole linked
section. Suppression removes cells, totals, percentages and derived association
statistics from both JSON and HTML. Safe null reasons remain visible. The source
record is unchanged. `.to_dict(small_cell_threshold=...)` exposes the explicit
projection threshold; `write_report` uses the established default projection.
Individual `CheckResult.to_dict()` remains more conservative than whole-report
table display. Aliases and suppression do not authenticate imported evidence.

`sensitive_details=True` must be supplied explicitly for each export, even when
input provenance says sensitive. Such HTML has the warning “Sensitive research
output: do not publish without review.” User strings are still escaped. Sensitive
reports do not silently write split plans, assignments, fit memberships or private
prediction records; those retain separate operational serializers.

The optional `write_findings_csv` uses the same projection and neutralizes
formula-leading text for human spreadsheet use. It is never generated silently.
It does not rewrite canonical keys or machine split TSV files.

## Write behavior and limitations

Choose an explicit local output directory. Existing named files cause a clear
refusal unless `overwrite=True`; unrelated files are retained. All content and
assets are prepared before writing, then staged and atomically replaced per file.
An exclusive directory lock prevents concurrent cooperating writers. Ordinary
replacement failures restore prior files. If storage also prevents rollback,
recovery copies remain in the named temporary directory for manual recovery.
This is not a multi-file power-loss transaction. A stale lock after process death
requires inspection before manual removal. Restrictive permissions are requested
where supported; Windows ACL inheritance still applies.

S08 is READY_FOR_REVIEW after its recorded checks, with human acceptance pending.
See {download}`the handoff <../state/handoffs/S08.md>` for exact evidence and unrun checks.
