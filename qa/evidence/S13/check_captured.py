"""Validate retained execution evidence, artifact digests and displayed synthetic numbers."""

import hashlib
import json
from pathlib import Path

from neurocvguard.models import AuditReport, EvaluationResult

evidence = Path(__file__).parent
records = json.loads((evidence / "executed/runs.json").read_text(encoding="utf-8"))
assert len(records) == 8
for row in records:
    directory = evidence / "executed" / row["name"]
    manifest = json.loads((directory / "demo.private.json").read_text(encoding="utf-8"))
    assert manifest["synthetic"] is True and manifest["execution_status"] == "completed"
    assert manifest["parameters"] == row["parameters"]
    for filename, digest in manifest["output_sha256"].items():
        assert hashlib.sha256((directory / filename).read_bytes()).hexdigest() == digest
    for name, summary in row["actual_metrics"].items():
        result = EvaluationResult.from_dict(
            json.loads((directory / name).read_text(encoding="utf-8"))
        )
        assert result.pooled_metrics.accuracy.value == summary["accuracy"]
        assert result.pooled_metrics.balanced_accuracy.value == summary["balanced_accuracy"]
        assert result.diagnostic_only == summary["diagnostic_only"]
    for path in directory.glob("*report.json"):
        report = AuditReport.from_dict(json.loads(path.read_text(encoding="utf-8")))
        html = path.with_suffix(".html").read_text(encoding="utf-8")
        assert "Fully synthetic demonstration" in html and "no patient data" in html
        if report.comparison_summary:
            for difference in report.comparison_summary.differences:
                displayed = "Null" if difference.difference is None else str(difference.difference)
                assert displayed in html
    # Capture normalization is explicit and restricted to private argv prefixes.
    assert any(token in str(manifest["command"]) for token in ("<PROJECT_ROOT>", "<USER_HOME>"))
    assert str(Path.home()).casefold() not in str(manifest["command"]).casefold()
    assert "command_path_redaction" in manifest
print(
    "8 retained runs: checksums, parameters, actual metrics and HTML values match. "
    "No screenshot claimed."
)
