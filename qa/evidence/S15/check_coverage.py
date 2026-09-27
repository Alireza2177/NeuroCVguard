"""Combine disjoint full-suite runs and enforce the unmodified specification gates."""

import json
from pathlib import Path

import coverage

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).parent
CORE = (
    "identity.py",
    "checks/cohort.py",
    "checks/partitions.py",
    "splitting.py",
    "_inner_plans.py",
    "fit_boundaries.py",
    "metrics.py",
    "_evaluation_inputs.py",
    "_evaluation_fits.py",
    "_tuning.py",
    "evaluation.py",
)


def main():
    measurement = coverage.Coverage(data_file=str(ROOT / ".coverage.s15-final"))
    measurement.combine(
        data_paths=[str(ROOT / ".coverage-s15" / str(i) / "data") for i in range(4)],
        strict=True,
        keep=True,
    )
    measurement.save()
    measurement.json_report(outfile=str(EVIDENCE / "coverage-final-data.json"))
    data = json.loads((EVIDENCE / "coverage-final-data.json").read_text())
    total = data["totals"]
    lines = total["covered_lines"] / total["num_statements"] * 100
    branches = total["covered_branches"] / total["num_branches"] * 100
    core = {}
    for name in CORE:
        matches = [
            value
            for path, value in data["files"].items()
            if path.replace("\\", "/").endswith("/neurocvguard/" + name)
        ]
        assert len(matches) == 1, name
        summary = matches[0]["summary"]
        core[name] = summary["covered_lines"] / summary["num_statements"] * 100
    record = {
        "package_line_percent": lines,
        "package_branch_percent": branches,
        "core_line_percent": core,
        "required": {"line": 90, "branch": 85, "core_line": 95},
        "exclusions_added": [],
        "passed": lines >= 90 and branches >= 85 and all(value >= 95 for value in core.values()),
    }
    (EVIDENCE / "coverage-gate.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    assert record["passed"], "Required coverage threshold not met; add meaningful tests."


if __name__ == "__main__":
    main()
