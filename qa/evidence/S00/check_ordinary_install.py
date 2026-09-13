"""Exercise the ordinary installed package outside the source directory."""

import json
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

probe = """
import importlib.metadata
import json
from pathlib import Path
import sys
import neurocvguard

distribution = importlib.metadata.distribution('neurocvguard')
assert distribution.version == neurocvguard.__version__ == '0.1.0'
assert Path(neurocvguard.__file__).is_relative_to(sys.prefix)
record = json.loads(distribution.read_text('direct_url.json'))
assert record['dir_info'].get('editable', False) is False
print('ordinary site-packages import: 0.1.0')
"""
console = Path(sysconfig.get_path("scripts")) / (
    "neurocvguard.exe" if sys.platform == "win32" else "neurocvguard"
)
with tempfile.TemporaryDirectory(prefix="neurocvguard-s00-") as directory:
    outcomes = []
    for command, expected in (
        ([sys.executable, "-I", "-B", "-c", probe], "ordinary site-packages import: 0.1.0"),
        ([sys.executable, "-I", "-m", "neurocvguard", "--version"], "neurocvguard 0.1.0"),
        ([str(console), "--version"], "neurocvguard 0.1.0"),
    ):
        result = subprocess.run(command, cwd=directory, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == expected
        assert result.stderr == ""
        outcomes.append({"exit_code": result.returncode, "stdout": result.stdout.strip()})
    assert not list(Path(directory).iterdir())
print(json.dumps(outcomes, indent=2))
