"""Probe the ordinary S06 installation outside the source tree."""

import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[3]
document = (root / "docs/association_diagnostics.md").read_text(encoding="utf-8")
example = document.split("```python\n", 1)[1].split("```", 1)[0]
probe = (
    """
from pathlib import Path
import sys
import neurocvguard
assert Path(neurocvguard.__file__).is_relative_to(sys.prefix)
"""
    + example
    + """
metadata['diagnosis'] = ['class-A'] * 10 + ['class-B'] * 10
cohort = Cohort(metadata, None, config.columns, tuple(metadata.observation_id))
checks = check_associations(cohort, config=config)
review = next(item for item in checks if item.rule_id == 'NCG-ASSOC-001')
assert review.evidence['statistic']['value'] == 1.0
assert review.status.value == 'fail'
assert review.to_dict()['evidence'] == {'details_omitted': True}
assert review.to_dict(sensitive_details=True)['evidence']['table'] == [[10, 0], [0, 10]]
assert list(Path.cwd().iterdir()) == []
print('PASS: installed S06 guide, V=0/V=1, support, warning and public/private evidence')
"""
)
with tempfile.TemporaryDirectory(prefix="neurocvguard-s06-") as directory:
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    print(result.stdout.strip())
