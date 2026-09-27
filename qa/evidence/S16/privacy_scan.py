"""Record review locations without echoing potentially sensitive matched values."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATTERNS = {
    "absolute_user_path": re.compile(r"[A-Za-z]:[\\/]+Users[\\/]|/home/|/Users/"),
    "email_like": re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    "credential_shape": re.compile(
        r"\b(?:AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,})\b"
    ),
    "participant_label_shape": re.compile(r"\b(?:sub|subject|patient)-\d{3,}\b", re.I),
}


def main():
    files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    hits, large = [], []
    for name in files:
        path = ROOT / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        if len(data) > 1_000_000:
            large.append(
                {"file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            )
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for kind, expression in PATTERNS.items():
                if expression.search(line):
                    hits.append({"file": name, "line": number, "kind": kind})
    record = {
        "scope": (
            "Tracked file review locations only; "
            "no proof of anonymity or exhaustive secret detection."
        ),
        "files_scanned": len(files),
        "hits": hits,
        "large_files": large,
    }
    with Path(__file__).with_name("privacy-scan-data.json").open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    print(
        f"Scanned {len(files)} tracked paths; {len(hits)} review locations; "
        f"{len(large)} large files."
    )


if __name__ == "__main__":
    main()
