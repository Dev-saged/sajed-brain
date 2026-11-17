#!/usr/bin/env python3
"""ماسح المشروع: فهرس رموز + نظافة + حرّاس. الاستخدام: scout.py <project> [--out DIR] [--fail-on error]."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from scoutlib.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
