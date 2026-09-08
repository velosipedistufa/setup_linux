#!/usr/bin/env python3
"""VRAM used/total + GDDR5 from hw.json."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ICON_VRAM, amdgpu_device, emit, g, read_hw, read_text  # noqa: E402


def main() -> None:
    dev = amdgpu_device()
    hw = read_hw()
    vtype = g("VRAM_TYPE") or hw.get("vram_type") or "GDDR5"
    if not dev:
        emit(f"{ICON_VRAM} --", "amdgpu sysfs missing", "down")
        return
    used = read_text(dev / "mem_info_vram_used")
    total = read_text(dev / "mem_info_vram_total")
    try:
        used_b = int(used)
        total_b = int(total)
    except (TypeError, ValueError):
        emit(f"{ICON_VRAM} --", "vram sysfs unreadable", "down")
        return
    used_g = used_b / (1024**3)
    total_g = total_b / (1024**3)
    pct = int(used_b * 100 / total_b) if total_b else 0
    text = f"{ICON_VRAM} {used_g:.1f}/{total_g:.0f}G {vtype}"
    tooltip = f"{used_b // (1024**2)} / {total_b // (1024**2)} MiB {vtype}\n{pct}%"
    cls = "ok"
    if pct >= 90:
        cls = "crit"
    elif pct >= 80:
        cls = "warn"
    emit(text, tooltip, cls, percentage=pct)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        emit(f"{ICON_VRAM} --", str(exc), "down")
