"""S09.C complete temporary-directory journey and library equivalence."""

import json
import shutil
from collections import Counter

from test_cli_commands import FIXTURES, process

from neurocvguard import audit_cohort, audit_splits, load_cohort, load_config, load_split_plan
from neurocvguard.checks.preprocessing import check_preprocessing
from neurocvguard.workflows import audit_workflow


def test_at_s09_09_complete_journey_and_api(tmp_path):
    work = tmp_path / "local journey ü"
    work.mkdir()
    for filename in (
        "config.json",
        "cohort_clean.tsv",
        "features_shuffled.tsv",
        "ledger_declared_global.json",
    ):
        shutil.copyfile(FIXTURES / filename, work / filename)
    shared = ["--cohort", "cohort_clean.tsv", "--config", "config.json"]
    feature = ["--features", "features_shuffled.tsv"]
    assert process(["init", "--out", "starter.json"], work).returncode == 0
    assert process(["validate", *shared, *feature], work).returncode == 0
    assert process(["audit", *shared, *feature, "--out", "cohort-audit"], work).returncode == 0
    assert process(["split", *shared, "--out", "splits"], work).returncode == 0
    args = [
        "audit",
        *shared,
        *feature,
        "--splits",
        "splits/plan.json",
        "--ledger",
        "ledger_declared_global.json",
        "--fail-on",
        "warning",
        "--out",
    ]
    module = process([*args, "module"], work)
    console = process([*args, "console"], work, "console")
    assert (module.returncode, module.stdout, module.stderr) == (
        console.returncode,
        console.stdout,
        console.stderr,
    )
    assert module.returncode == 3  # Declared global fitting has warning severity.
    config = load_config(work / "config.json")
    cohort = load_cohort(
        work / "cohort_clean.tsv", config=config, features=work / "features_shuffled.tsv"
    )
    plan = load_split_plan(work / "splits/plan.json", cohort=cohort, config=config)
    ledger = json.loads((work / "ledger_declared_global.json").read_text())
    result = audit_workflow(cohort, config=config, plan=plan, ledger=ledger)
    actual = json.loads((work / "module/report.json").read_text())
    assert actual == result.to_dict()
    assert (work / "module/report.json").read_bytes() == (work / "console/report.json").read_bytes()
    # Independently account for every scoped upstream API check, including repeated rules.
    expected = []
    for report in (audit_cohort(cohort, config=config), audit_splits(cohort, plan, config=config)):
        expected.extend(
            check for check in report.checks if not check.rule_id.startswith("NCG-PROV-")
        )
    expected.extend(check_preprocessing(cohort, config=config, plan=plan, ledger=ledger))

    def signatures(checks):
        return Counter(
            json.dumps(
                {k: v for k, v in item._as_dict().items() if k != "instance_id"}, sort_keys=True
            )
            for item in checks
        )

    assert signatures(result.checks) == signatures(expected)
    assert (
        process(["report", "--input", "module/report.json", "--out", "render"], work).returncode
        == 0
    )
    assert (work / "render/report.json").read_bytes() == (work / "module/report.json").read_bytes()


def test_at_s09_01_findings_exit_parity(tmp_path):
    args = [
        "audit",
        "--cohort",
        str(FIXTURES / "cohort_clean.tsv"),
        "--config",
        str(FIXTURES / "config.json"),
        "--splits",
        str(FIXTURES / "splits_participant_overlap.json"),
        "--out",
    ]
    module = process([*args, str(tmp_path / "module")], tmp_path)
    console = process([*args, str(tmp_path / "console")], tmp_path, "console")
    assert (module.returncode, module.stdout, module.stderr) == (
        console.returncode,
        console.stdout,
        console.stderr,
    )
    assert module.returncode == 3
    assert (tmp_path / "module/report.json").read_bytes() == (
        tmp_path / "console/report.json"
    ).read_bytes()
