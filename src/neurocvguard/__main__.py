"""Minimal version entry point for the development bootstrap."""

import argparse
from collections.abc import Sequence

from neurocvguard import __version__


def main(argv: Sequence[str] | None = None) -> int:
    """Display bootstrap help or the local package version.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments to parse; None uses the process arguments.

    Returns
    -------
    int
        Zero after displaying help with no arguments.

    Raises
    ------
    SystemExit
        Zero for explicit help/version; two for invalid arguments.

    Notes
    -----
    Only help and version are available in S00. No research data are read.

    Examples
    --------
    Run ``python -m neurocvguard --version`` to print the local version.
    """
    parser = argparse.ArgumentParser(
        prog="neurocvguard",
        description="Research-only development bootstrap. Only help and version are available.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
