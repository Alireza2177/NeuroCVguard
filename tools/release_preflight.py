"""Read-only local S17 checkpoint. This tool never grants publication permission."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
from pathlib import Path
from typing import Any


def inspect_candidate(root: Path, dist: Path, manifest: Path | None = None) -> dict[str, Any]:
    """Report unresolved owner gates and drift from an explicitly selected candidate."""
    status = json.loads((root / "state/PROJECT_STATUS.json").read_text(encoding="utf-8"))
    metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    release = metadata["tool"]["neurocvguard"]["release"]
    retained = json.loads(
        (manifest or root / "qa/evidence/S16/distributions.json").read_text(encoding="utf-8")
    )
    if manifest is None:
        preservation = json.loads((root / "qa/evidence/S16/preservation.json").read_text())
    else:
        preservation = retained
        required = {"pyproject.toml", "README.md", "LICENSE", ".gitignore"}
        if set(preservation.get("candidate_metadata_hashes", {})) != required:
            raise ValueError("Selected candidate must record all four metadata hashes")
    blockers = []
    for field in (
        "license-status",
        "copyright-owner",
        "maintainer",
        "security-contact",
        "repository-url",
        "package-namespace",
    ):
        value = release.get(field)
        if not isinstance(value, str) or not value.strip() or "PENDING" in value.upper():
            blockers.append(f"Owner confirmation missing: {field}")
    if "NOT FINALIZED" in (root / "LICENSE").read_text(encoding="utf-8"):
        blockers.append("LICENSE is a proposal, not a finalized grant")
    if status.get("public_release_authorized") is not True:
        blockers.append("Project public-release authorization is absent")
    pending = [
        s["id"]
        for s in status["stages"]
        if s["id"] != "S17" and s.get("human_accepted") is not True
    ]
    if pending:
        blockers.append("Human stage acceptance pending: " + ", ".join(pending))
    if status["target_release"] != retained["version"]:
        blockers.append("Target version differs from retained candidate")

    artifacts = []
    for item in retained["artifacts"]:
        name = item["file"]
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("Candidate artifact name must be a basename")
        path = dist / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        matches = digest == item["sha256"] and path.stat().st_size == item["bytes"]
        if not matches:
            blockers.append(f"Retained artifact missing or changed: {name}")
        artifacts.append({"file": name, "sha256": digest, "matches_candidate": matches})
    drift = []
    for name, expected in retained["source_payload_hashes"].items():
        relative = (
            name.replace("neurocvguard/examples/", "examples/", 1)
            if name.startswith("neurocvguard/examples/")
            else "src/" + name
        )
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("Candidate source path escapes project")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            drift.append(relative)
    for name, expected in preservation["candidate_metadata_hashes"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("Candidate metadata path escapes project")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            drift.append(name)
    if drift:
        blockers.append("Source/metadata changed: rebuild and review new candidate hashes")
    return {
        "scope": "Local consistency only; cannot authenticate a human or grant permission.",
        "status": "BLOCKED" if blockers else "LOCAL_CHECKS_PASS_REQUIRES_HUMAN_DECISION",
        "publication_performed": False,
        "version": retained["version"],
        "blockers": blockers,
        "source_drift": sorted(drift),
        "artifacts": artifacts,
        "still_requires": [
            "Owner-verified namespaces and visibility",
            "Exact final commit and artifact approval",
            "Human scientific/usability review",
            "Authorization for each external action",
            "Public artifact/download/install verification after approved publication",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, help="New reviewed archive audit; defaults to S16")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Evidence output already exists; choose a new path")
    record = inspect_candidate(args.root, args.dist, args.manifest)
    record["checked_revision"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=args.root, text=True
    ).strip()
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    print(json.dumps(record, indent=2))
    return 3 if record["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
