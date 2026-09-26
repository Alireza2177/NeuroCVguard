"""Verify exact report asset bytes in both built distribution formats."""

import hashlib
import json
import sys
import tarfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[3]
dist = Path(__file__).parent / (sys.argv[1] if len(sys.argv) > 1 else "dist")
wheel = next(dist.glob("*.whl"))
sdist = next(dist.glob("*.tar.gz"))
result = {}
with zipfile.ZipFile(wheel) as archive, tarfile.open(sdist) as source:
    for name in (
        "templates/report.html",
        "templates/report.css",
        "_projection.py",
        "_report_tables.py",
        "reporting.py",
    ):
        relative = "neurocvguard/" + name
        expected = (root / "src" / relative).read_bytes()
        assert archive.read(relative) == expected
        member = next(
            item for item in source.getmembers() if item.name.endswith("/src/" + relative)
        )
        handle = source.extractfile(member)
        assert handle is not None
        with handle:
            assert handle.read() == expected
        result[name] = hashlib.sha256(expected).hexdigest()
print(json.dumps({"wheel_and_sdist_assets_match_source": result}, indent=2))
