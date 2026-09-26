"""Check that screenshots' HTML still matches the final installed renderer."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).parent
result = {}
with tempfile.TemporaryDirectory(prefix="neurocvguard-s08-rerender-") as directory:
    process = subprocess.run(
        [sys.executable, "-I", "-B", str(root / "render_fixtures.py"), directory],
        capture_output=True,
        text=True,
    )
    assert process.returncode == 0, process.stderr
    for name in ("public", "sensitive"):
        for artifact in ("report.html", "report.json", "report.manifest.json"):
            actual = (Path(directory) / name / artifact).read_bytes()
            expected = (root / "rendered" / name / artifact).read_bytes()
            assert actual == expected, (name, artifact)
            result[f"{name}/{artifact}"] = hashlib.sha256(actual).hexdigest()
print(json.dumps({"reviewed_html_matches_final_renderer": result}, indent=2))
