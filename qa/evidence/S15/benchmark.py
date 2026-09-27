"""Separate deterministic CPU workloads, measuring time and OS peak working set."""

import ctypes
import json
import os
import platform
import subprocess
import sys
import time
from ctypes import wintypes
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from neurocvguard import audit_cohort, evaluate_baseline, load_cohort, make_splits
from neurocvguard.checks.cohort import inventory_cohort
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.synthetic import SyntheticParameters, generate_synthetic


def peak_memory():
    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            *[
                (name, ctypes.c_size_t)
                for name in (
                    "PeakWorkingSetSize",
                    "WorkingSetSize",
                    "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage",
                    "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage",
                    "PagefileUsage",
                    "PeakPagefileUsage",
                )
            ],
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    if not psapi.GetProcessMemoryInfo(
        kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return counters.PeakWorkingSetSize


def child(workload):
    rows = 100000 if workload == "inventory-100k" else 10000
    if workload == "baseline":
        data = generate_synthetic(SyntheticParameters(n_participants=120, n_features=12))
        config = data.config()
        cohort = load_cohort(data.metadata, config=config, features=data.features)
        plan = make_splits(cohort, config=config)
        start = time.perf_counter()
        result = evaluate_baseline(cohort, plan, config=config)
        measured = {
            "execution_status": result.execution_status.value,
            "rows": 240,
            "participants": 120,
            "features": 12,
            "folds": len(plan.folds),
        }
        assert result.execution_status == "completed"
    else:
        metadata = pd.DataFrame(
            {
                "observation_id": [f"SYN-o{i:06}" for i in range(rows)],
                "subject_id": [f"SYN-p{i // 2:06}" for i in range(rows)],
                "diagnosis": [str(i // 2 % 2) for i in range(rows)],
                "session_id": [f"visit{i % 2}" for i in range(rows)],
                "site": [f"SYN-site{i // 4 % 5}" for i in range(rows)],
                "family": [f"SYN-family{i // 4:06}" for i in range(rows)],
            }
        )
        config = AuditConfig(columns=ColumnMap(independence=("family",)))
        cohort = load_cohort(metadata, config=config)
        start = time.perf_counter()
        if workload.startswith("inventory"):
            inventory = inventory_cohort(cohort)
            assert inventory.n_observations == rows and inventory.n_participants == rows // 2
        elif workload == "audit-10k":
            report = audit_cohort(cohort, config=config)
            assert report.input_summary["n_observations"] == rows
        elif workload == "split-10k":
            plan = make_splits(cohort, config=config)
            assert sum(len(f.test_ids) for f in plan.folds) == rows
        else:
            raise ValueError(workload)
        measured = {
            "rows": rows,
            "participants": rows // 2,
            "features": 0,
            "protected_components": rows // 4,
        }
    measured.update(
        workload=workload,
        elapsed_seconds=time.perf_counter() - start,
        process_peak_working_set_bytes=peak_memory(),
    )
    print(json.dumps(measured))


def main():
    if len(sys.argv) > 1:
        child(sys.argv[1])
        return
    destination = Path(__file__).with_name("benchmark-results.json")
    if destination.exists():
        raise FileExistsError(destination)
    measurements = []
    for workload in ("inventory-10k", "inventory-100k", "audit-10k", "split-10k", "baseline"):
        for repeat in range(2):
            command = [sys.executable, __file__, workload]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            row = json.loads(result.stdout)
            row.update(
                repeat=repeat,
                exit_code=result.returncode,
                command=["<ENV_PYTHON>", "qa/evidence/S15/benchmark.py", workload],
            )
            measurements.append(row)
            print(json.dumps(row), flush=True)
    record = {
        "hardware": {
            "processor": platform.processor(),
            "logical_cpus": os.cpu_count(),
            "architecture": platform.machine(),
            "os": platform.platform(),
        },
        "versions": {
            name: version(name)
            for name in ("neurocvguard", "numpy", "pandas", "scipy", "scikit-learn")
        },
        "python": platform.python_version(),
        "seed": 2026,
        "measurements": measurements,
        "measurement_scope": "Operation elapsed time excludes input construction/loading; "
        "OS process peak working set includes interpreter, imports and input construction. "
        "Two separate child processes per workload; no universal timing target.",
    }
    destination.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
