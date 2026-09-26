"""Check installed report assets and the guide outside the source tree."""

import subprocess
import sys
import tempfile
from pathlib import Path

document = (Path(__file__).resolve().parents[3] / "docs/reporting.md").read_text(encoding="utf-8")
example = document.split("```python\n", 1)[1].split("```", 1)[0]
probe = (
    "from pathlib import Path\nimport sys\nimport neurocvguard\n"
    "from importlib.resources import files\n"
    "assert Path(neurocvguard.__file__).is_relative_to(sys.prefix)\n"
    "for name in ('report.html', 'report.css'):\n"
    "    assert files('neurocvguard').joinpath('templates', name).read_text()\n"
    + example
    + "\nassert list(Path.cwd().iterdir()) == []\n"
    "print('PASS: installed assets, public JSON/HTML, rerender and optional CSV guide')\n"
)
with tempfile.TemporaryDirectory(prefix="neurocvguard-s08-") as directory:
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    print(result.stdout.strip())
