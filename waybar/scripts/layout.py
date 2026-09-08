#!/usr/bin/env python3
"""en/ru from dwl ($XDG_RUNTIME_DIR/dwl-layout). Compositor is source of truth."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import emit, read_text  # noqa: E402


def main() -> None:
    rt = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    raw = (read_text(Path(rt) / "dwl-layout") or "").strip().lower()
    if raw not in ("en", "ru"):
        emit("??", "layout unknown until dwl writes $XDG_RUNTIME_DIR/dwl-layout", "unknown")
        return
    names = {
        "en": "en · display only (Ctrl+Shift in dwl)",
        "ru": "ru · display only (Ctrl+Shift in dwl)",
    }
    emit(raw, names[raw], raw)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        emit("??", str(exc), "unknown")
