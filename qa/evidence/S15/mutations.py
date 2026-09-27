"""Ten specified scientific faults in isolated copies; require failure and restoration.

Never patch the active source tree. Each mutant runs in a fresh interpreter with
an isolated PYTHONPATH and imported-location assertion. Temporary copies are
owned by TemporaryDirectory. Keep exact diffs, exit codes and test diagnostics.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).parent
CASES = [
    (
        "row_order_join",
        "_features.py",
        "aligned = data.set_index(key).loc[list(order), list(names)].reset_index()",
        "aligned = data[[key, *names]].copy()",
        "tests/test_feature_inputs.py::test_at_s02_08_shuffled_feature_rows",
    ),
    (
        "participant_session_tuple",
        "checks/partitions.py",
        "overlap = train_people & test_people",
        "overlap = {(context.people[k], context.labels['session'][k]) for k in train} & "
        "{(context.people[k], context.labels['session'][k]) for k in test}",
        "tests/test_partitions.py::test_at_s04_01_participant_overlap_without_observation_overlap",
    ),
    (
        "global_session_identity",
        "checks/partitions.py",
        "overlap = train_people & test_people",
        "overlap = {context.labels['session'][k] for k in train} & "
        "{context.labels['session'][k] for k in test}",
        "tests/test_partitions.py::test_at_s04_02_clean_repeated_cohort",
    ),
    (
        "tuple_not_transitive",
        "identity.py",
        "key = (column, value)",
        "key = (column, value, person)",
        "tests/test_identity.py::test_at_s03_05_transitive_components",
    ),
    (
        "global_scaler",
        "_evaluation_fits.py",
        "pipeline.fit(training, targets, classifier__sample_weight=weights)",
        "pipeline.fit(training, targets, classifier__sample_weight=weights)\n"
        "            pipeline.named_steps['scaler'].fit(inputs.features.fillna(0))",
        "tests/test_evaluation_fits.py::test_at_s10_01_training_only_scaler",
    ),
    (
        "outer_test_in_inner_fit",
        "_evaluation_fits.py",
        "else inputs.features.loc[list(inner.train_ids)].copy()",
        "else inputs.features.copy()",
        "tests/test_nested_runner.py::test_at_s11_01_actual_imputer_scaler_and_pipeline_inputs",
    ),
    (
        "drop_held_out_site",
        "splitting.py",
        "positions = LeaveOneGroupOut().split("
        "np.zeros((len(table.people), 1)), table.targets, domains)",
        "positions = list(LeaveOneGroupOut().split(\n"
        "        np.zeros((len(table.people), 1)), table.targets, domains))[1:]",
        "tests/test_domain_generation.py::test_at_s05_06_held_out_phase[site]",
    ),
    (
        "undefined_auc_zero",
        "metrics.py",
        'auc = MetricValue(None, "missing_true_class", n)',
        "auc = MetricValue(0.0, None, n)",
        "tests/test_evaluation_metrics.py::test_at_s10_09_single_class_test",
    ),
    (
        "hide_failed_fold",
        "evaluation.py",
        "folds=tuple(folds),",
        'folds=tuple(f for f in folds if f.status == "completed"),',
        "tests/test_evaluation_runner.py::test_at_s10_13_failed_fold_never_easy_fold_average",
    ),
    (
        "hidden_html_id_leak",
        "reporting.py",
        "return _render(_project(result, sensitive_details), sensitive_details)",
        "return _render(_project(result, sensitive_details), sensitive_details) + "
        "'<script type=\"application/json\">' + "
        "json.dumps(result.to_dict(sensitive_details=True)) + '</script>'",
        "tests/test_report_projection.py::test_at_s08_01_default_id_redaction",
    ),
]


def main():
    destination = EVIDENCE / "mutation-results.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = []
    with tempfile.TemporaryDirectory(prefix="neurocvguard-mutations-") as temporary:
        root = Path(temporary)
        for directory in ("src", "tests", "fixtures"):
            shutil.copytree(
                ROOT / directory,
                root / directory,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        shutil.copyfile(ROOT / "pyproject.toml", root / "pyproject.toml")
        environment = dict(
            os.environ,
            PYTHONPATH=str(root / "src"),
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONIOENCODING="utf-8",
        )
        location = subprocess.run(
            [sys.executable, "-c", "import neurocvguard; print(neurocvguard.__file__)"],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        assert str(root / "src") in location.stdout
        for name, relative, old, new, node in CASES:
            path = root / "src/neurocvguard" / relative
            original = path.read_bytes()
            text = original.decode("utf-8")
            assert text.count(old) == 1, (name, text.count(old))
            path.write_text(text.replace(old, new), encoding="utf-8")
            command = [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--strict-markers",
                "--strict-config",
                "-p",
                "no:cacheprovider",
                node,
            ]
            try:
                mutant = subprocess.run(
                    command,
                    cwd=root,
                    env=environment,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
            finally:
                path.write_bytes(original)
            restored = subprocess.run(
                command, cwd=root, env=environment, capture_output=True, text=True, encoding="utf-8"
            )

            def normalized(value):
                return (
                    value.replace(str(root), "<ISOLATED_COPY>")
                    .replace(str(ROOT), "<PROJECT_ROOT>")
                    .replace(str(Path.home()), "<USER_HOME>")
                )

            record = {
                "fault": name,
                "file": "src/neurocvguard/" + relative,
                "old": old,
                "new": new,
                "test": node,
                "command": ["<ENV_PYTHON>", *command[1:]],
                "mutant_exit": mutant.returncode,
                "restored_exit": restored.returncode,
                "mutant_stdout": normalized(mutant.stdout),
                "mutant_stderr": normalized(mutant.stderr),
                "restored_stdout": normalized(restored.stdout),
                "restored_stderr": normalized(restored.stderr),
                "source_sha256": hashlib.sha256(original).hexdigest(),
                "restored_identically": path.read_bytes() == original,
            }
            records.append(record)
            print(name, mutant.returncode, restored.returncode, flush=True)
            assert mutant.returncode == 1 and restored.returncode == 0, record
            assert "FAILED" in mutant.stdout or "ERROR" in mutant.stdout
        with destination.open("x", encoding="utf-8") as handle:
            json.dump(records, handle, indent=2)
            handle.write("\n")
    print(f"Detected and restored {len(records)} / {len(CASES)} faults.")


if __name__ == "__main__":
    main()
