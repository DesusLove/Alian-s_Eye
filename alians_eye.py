#!/usr/bin/python3
"""Backward-compatible launcher. Prefer `pip install alien's-eye` and the
`alians_eye` command; this shim keeps `python alians_eye.py` working from a
source checkout."""

if __name__ == "__main__":
    import sys
    from pathlib import Path

    src_dir = Path(__file__).resolve().parent / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
    # Drop this shim from sys.modules so the real package can be imported.
    sys.modules.pop("alians_eye", None)

    from alians_eye.cli import main

    main()
