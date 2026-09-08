#!/usr/bin/env python3
"""LAN device count from IPv4 ARP/neigh on the physical NIC. Optional broadcast ping."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import cache_dir, emit, g, physical_ifaces, read_text, run, save_json, load_json  # noqa: E402

STAMP = cache_dir() / "lan-broadcast.json"
BCAST_EVERY = 120


def iface() -> str | None:
    names = physical_ifaces()
    for name in names:
        if read_text(f"/sys/class/net/{name}/operstate") == "up":
            return name
    return names[0] if names else None


def maybe_broadcast(dev: str) -> None:
    st = load_json(STAMP) or {}
    now = time.time()
    if now - float(st.get("ts") or 0) < BCAST_EVERY:
        return
    # Refresh ARP. Routers may ignore this; tooltip is honest.
    bcast = g("LAN_BCAST")
    if not bcast:
        home = g("HOME_SERVER")
        if home.count(".") == 3:
            bcast = ".".join(home.split(".")[:3] + ["255"])
    if not bcast:
        return
    run(["ping", "-c", "1", "-W", "1", "-b", bcast], timeout=2)
    save_json(STAMP, {"ts": now, "dev": dev})


def neigh(dev: str) -> list[tuple[str, str]]:
    proc = run(["ip", "-j", "-4", "neigh", "show", "dev", dev], timeout=2)
    rows = []
    if proc.returncode == 0 and proc.stdout.strip():
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            data = []
        for n in data:
            dst = n.get("dst")
            ll = n.get("lladdr")
            state = (n.get("state") or [""])[0] if isinstance(n.get("state"), list) else n.get("state")
            if not dst or not ll:
                continue
            if str(state).upper() == "FAILED":
                continue
            rows.append((dst, ll))
    if rows:
        return rows
    # fallback text parse
    proc = run(["ip", "-4", "neigh", "show", "dev", dev], timeout=2)
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) < 5 or "lladdr" not in parts:
            continue
        if "FAILED" in parts:
            continue
        dst = parts[0]
        ll = parts[parts.index("lladdr") + 1]
        rows.append((dst, ll))
    return rows


def main() -> None:
    dev = iface()
    if not dev:
        emit("LAN", "no physical iface", "down")
        return
    maybe_broadcast(dev)
    rows = neigh(dev)
    # unique IPv4
    seen = {}
    for ip, mac in rows:
        seen[ip] = mac
    tooltip = (
        "ARP recently seen on "
        + dev
        + " (not a full LAN census)\n"
    )
    if seen:
        tooltip += "\n".join(f"{ip}  {mac}" for ip, mac in sorted(seen.items()))
    else:
        tooltip += "(none)"
    emit("LAN", tooltip, "ok" if seen else "warn")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        emit("n?", str(exc), "down")
