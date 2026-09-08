#!/usr/bin/env python3
"""CPU load for 4 physical cores. HT siblings are merged, never shown as 8 cores."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import cache_dir, emit, load_json, save_json  # noqa: E402

CACHE = cache_dir() / "cpu-stat.json"
# Xeon E3-1270 V2: core i uses cpu i and cpu i+4
SIBLINGS = ((0, 4), (1, 5), (2, 6), (3, 7))


def read_proc() -> tuple[tuple[int, int], dict[int, tuple[int, int]]]:
    total = (0, 0)
    cpus: dict[int, tuple[int, int]] = {}
    with open("/proc/stat", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("cpu"):
                break
            parts = line.split()
            name = parts[0]
            nums = [int(x) for x in parts[1:]]
            idle = nums[3] + (nums[4] if len(nums) > 4 else 0)
            tot = sum(nums)
            busy = tot - idle
            if name == "cpu":
                total = (busy, tot)
            else:
                cpus[int(name[3:])] = (busy, tot)
    return total, cpus


def pct(now: tuple[int, int], prev: tuple[int, int]) -> int:
    db = now[0] - prev[0]
    dt = now[1] - prev[1]
    if dt <= 0:
        return 0
    return max(0, min(100, int(db * 100 / dt)))


def main() -> None:
    total_now, cpus_now = read_proc()
    prev = load_json(CACHE) or {}
    save_json(
        CACHE,
        {
            "total": list(total_now),
            "cpus": {str(k): list(v) for k, v in cpus_now.items()},
        },
    )
    if not prev:
        emit("… ", "CPU sampling…", "ok")
        return

    prev_total = tuple(prev.get("total") or [0, 0])
    prev_cpus = {int(k): tuple(v) for k, v in (prev.get("cpus") or {}).items()}
    overall = pct(total_now, prev_total)

    lines = ["CPU  4 physical cores (HT merged, not 8 threads)"]
    core_pcts = []
    for i, (a, b) in enumerate(SIBLINGS):
        na = cpus_now.get(a, (0, 0))
        nb = cpus_now.get(b, (0, 0))
        pa = prev_cpus.get(a, (0, 0))
        pb = prev_cpus.get(b, (0, 0))
        # Combine sibling counters = physical core
        now = (na[0] + nb[0], na[1] + nb[1])
        old = (pa[0] + pb[0], pa[1] + pb[1])
        p = pct(now, old)
        core_pcts.append(p)
        bar = "█" * (p // 10) + "▁" * (10 - p // 10)
        lines.append(f"core {i}  {p:3d}%  {bar}")

    cls = "ok"
    if overall >= 90:
        cls = "crit"
    elif overall >= 70:
        cls = "warn"
    emit(f"{overall}% ", "\n".join(lines), cls, percentage=overall)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        emit("cpu --", str(exc), "down")
