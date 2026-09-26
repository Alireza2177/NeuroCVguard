"""Allowlisted presentation of precomputed association evidence; no statistics are run."""

import math
from collections.abc import Mapping

from neurocvguard.models import CheckResult
from neurocvguard.serialization import JSONObject, JSONValue


def association_display(
    check: CheckResult, threshold: int, aliases: dict[str, dict[str, str]]
) -> JSONObject | None:
    """Return only validated, unsuppressed display cells and local domain aliases.

    A zero cell also conservatively suppresses the section, preserving the earlier
    S06 boundary. Individual CheckResult projection remains deliberately minimal.
    Whole-report projection can add this allowlisted display section.
    """
    if not check.rule_id.startswith("NCG-ASSOC-"):
        return None
    raw = check.evidence.get("display_table")
    # Reprojecting public records must be idempotent, without trusting their labels.
    public = isinstance(raw, Mapping)
    source = raw if public else check.evidence
    assert isinstance(source, Mapping)
    table = source.get("counts" if public else "table")
    targets = source.get("target_levels")
    rows = source.get("row_levels")
    if not isinstance(table, (tuple, list)) or not table or len(table) > 100:
        return None
    if not isinstance(rows, (tuple, list)) or len(rows) != len(table):
        return None
    if not isinstance(targets, (tuple, list)) or not targets or len(targets) > 100:
        return None
    if any(not isinstance(level, str) for level in (*rows, *targets)):
        return None
    counts: list[JSONValue] = []
    for row in table:
        if not isinstance(row, (tuple, list)) or len(row) != len(targets):
            return None
        checked: list[JSONValue] = []
        for cell in row:
            if type(cell) is not int or cell < threshold:
                return None
            checked.append(cell)
        counts.append(checked)
    statistic = source.get("statistic")
    if not isinstance(statistic, Mapping):
        return None
    value = statistic.get("value")
    if value is not None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return None
        if not math.isfinite(value) or not 0 <= value <= 1:
            return None
    if value is None and statistic.get("reason") != "constant_variable":
        return None
    role = check.scope.get("field", "")
    label = "Site" if role == "site" else "Phase" if role == "phase" else "Category"
    # Alias target levels too: safe for arbitrary imported text, with no reverse map.
    # Semantic class names remain available in explicit sensitive output.
    return {
        "row_levels": [aliases[label][str(level)] for level in rows],
        "target_levels": [f"Target {index + 1:02}" for index in range(len(targets))],
        "counts": counts,
        "statistic": {
            "value": value,
            "reason": "constant_variable" if value is None else None,
        },
        "counting_unit": "participant",
        "estimator": "Cramer's V; uncorrected Pearson chi-square; correction=False",
    }
