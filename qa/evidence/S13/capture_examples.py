"""Execute every tutorial in fresh temporary outputs and retain actual synthetic artifacts."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[3]
destination = Path(__file__).parent / "executed"
assert not destination.exists(), "Never overwrite captured evidence"
destination.mkdir()
records = []


def normalize_private_command(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    original = document["command"]
    document["command"] = [
        arg.replace(str(root), "<PROJECT_ROOT>")
        .replace(str(Path.home()), "<USER_HOME>")
        .replace(str(work), "<RUN_DIRECTORY>")
        for arg in original
    ]
    document["command_path_redaction"] = (
        "Only machine-specific prefixes in argv; output bytes unchanged."
    )
    path.write_text(json.dumps(document, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


with tempfile.TemporaryDirectory(prefix="ncg-s13-examples-") as directory:
    work = Path(directory)
    scripts = sorted((root / "examples").glob("[0-9][0-9]_*.py"))
    commands = [
        (script.stem, [str(script), "--out", script.stem, "--sensitive-details"])
        for script in scripts
    ]
    commands += [
        (
            f"demo-{scenario}",
            ["-m", "neurocvguard", "demo", "--scenario", scenario, "--out", f"demo-{scenario}"],
        )
        for scenario in ("clean", "repeated", "site_shift")
    ]
    for name, args in commands:
        command = [sys.executable, "-I", *args]
        completed = subprocess.run(
            command,
            cwd=work,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        record = {
            "name": name,
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        print(json.dumps(record, ensure_ascii=True), flush=True)
        assert completed.returncode == 0, record
        source = work / name
        manifest = json.loads((source / "demo.private.json").read_text(encoding="utf-8"))
        for filename, checksum in manifest["output_sha256"].items():
            assert hashlib.sha256((source / filename).read_bytes()).hexdigest() == checksum
        metrics = {}
        for path in source.glob("*.evaluation.private.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            metrics[path.name] = {
                "objective": data["objective"],
                "diagnostic_only": data["diagnostic_only"],
                "execution_status": data["execution_status"],
                "accuracy": data["pooled_metrics"]["accuracy"]["value"],
                "balanced_accuracy": data["pooled_metrics"]["balanced_accuracy"]["value"],
            }
        shutil.copytree(source, destination / name)
        normalize_private_command(destination / name / "demo.private.json")
        records.append(
            {
                "name": name,
                "exit_code": completed.returncode,
                "actual_metrics": metrics,
                "parameters": manifest["parameters"],
                "versions": manifest["versions"],
            }
        )
    # Normalize the early smoke's actual argv too; it is explicitly intermediate evidence.
    normalize_private_command(Path(__file__).parent / "smoke-clean/demo.private.json")

(destination / "runs.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
print(
    f"Retained {len(records)} actual runs with verified artifact checksums; no screenshot claimed."
)
