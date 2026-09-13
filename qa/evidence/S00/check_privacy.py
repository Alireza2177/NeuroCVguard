"""Scan S00 text artifacts for a narrow set of accidental privacy exposures."""

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[3]
files = [
    root / name
    for name in (
        "README.md",
        "LICENSE",
        "AI_ASSISTANCE.md",
        "pyproject.toml",
        ".gitignore",
        "state/handoffs/S00.md",
        "state/PROJECT_STATUS.json",
        "qa/case_to_test_map.json",
    )
]
files += list((root / "src/neurocvguard").glob("*.py"))
files += list((root / "tests").glob("*.py"))
files += [
    path
    for path in (root / "qa/evidence/S00").iterdir()
    if path.is_file() and path.suffix in {".json", ".xml", ".md", ".py"}
]
patterns = {
    "absolute_user_path": r"(?i)[A-Z]:[\\/]+users[\\/]+",
    "private_key": r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
    "credential_token": r"\b(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_]{16,}",
}
findings = []
for path in files:
    body = path.read_text(encoding="utf-8")
    for label, pattern in patterns.items():
        if re.search(pattern, body):
            findings.append({"file": path.relative_to(root).as_posix(), "pattern": label})
assert not findings, findings
print(json.dumps({"files_examined": len(files), "findings": findings, "proof_of_anonymity": False}))
