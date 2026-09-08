#!/usr/bin/env python3
"""RX580 gpu_busy_percent + hover clocks/temp/power. 2s sysfs, no radeontop."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ICON_GPU, amdgpu_device, emit, read_text  # noqa: E402


def starred_clock(path: Path) -> str | None:
    raw = read_text(path)
    if not raw:
        return None
    for line in raw.splitlines():
        if "*" in line:
            # "2: 952Mhz *"
            parts = line.split()
            if len(parts) >= 2:
                return parts[1]
    return None


def hwmon_edge_ppt(dev: Path) -> tuple[str | None, str | None]:
    temp = power = None
    for hw in (dev / "hwmon").glob("hwmon*"):
        t = read_text(hw / "temp1_input")
        if t and t.isdigit():
            temp = f"{int(t) / 1000:.0f}°C"
        p = read_text(hw / "power1_input")
        if p and p.isdigit():
            power = f"{int(p) / 1_000_000:.0f} W"
    return temp, power


def main() -> None:
    dev = amdgpu_device()
    if not dev:
        emit(f"{ICON_GPU} --", "amdgpu sysfs missing", "down")
        return
    busy = read_text(dev / "gpu_busy_percent")
    try:
        pct = int(busy) if busy is not None else None
    except ValueError:
        pct = None
    if pct is None:
        emit(f"{ICON_GPU} --", f"unreadable {dev}", "down")
        return

    sclk = starred_clock(dev / "pp_dpm_sclk") or "?"
    mclk = starred_clock(dev / "pp_dpm_mclk") or "?"
    temp, ppt = hwmon_edge_ppt(dev)
    tooltip = "\n".join(
        [
            f"GPU {pct}%",
            f"sclk {sclk}",
            f"mclk {mclk}",
            f"edge {temp or '?'}",
            f"PPT {ppt or '?'}",
            str(dev),
        ]
    )
    cls = "ok"
    if pct >= 90:
        cls = "crit"
    elif pct >= 75:
        cls = "warn"
    emit(f"{ICON_GPU} {pct}%", tooltip, cls, percentage=pct)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        emit(f"{ICON_GPU} --", str(exc), "down")
