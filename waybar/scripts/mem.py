#!/usr/bin/env python3
"""RAM used % + type from DMI (cached; re-probed if the board changes)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import emit, hw_info  # noqa: E402


def kB(meminfo: dict[str, int], key: str) -> int:
    return meminfo.get(key, 0)


def main() -> None:
    info: dict[str, int] = {}
    with open("/proc/meminfo", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                info[parts[0].rstrip(":")] = int(parts[1])
    total = kB(info, "MemTotal")
    avail = kB(info, "MemAvailable")
    if total <= 0:
        emit("ram --", "MemTotal missing", "down")
        return
    used = total - avail
    pct = int(used * 100 / total)
    rtype = hw_info().get("ram_type") or "?"
    used_g = used / (1024 * 1024)
    total_g = total / (1024 * 1024)
    cls = "ok"
    if pct >= 92:
        cls = "crit"
    elif pct >= 80:
        cls = "warn"
    emit(
        f"{pct}%  {rtype}",
        f"RAM {used_g:.1f}G/{total_g:.1f}G {rtype}",
        cls,
        percentage=pct,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        emit("ram --", str(exc), "down")
