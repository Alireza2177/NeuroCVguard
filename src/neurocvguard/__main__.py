"""Module and installed console entry points share the same CLI."""

from neurocvguard.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
