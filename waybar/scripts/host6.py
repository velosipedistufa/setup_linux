#!/usr/bin/env python3
"""Home-server reachability. Address from globals.sh."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import emit, g, ping_host  # noqa: E402


def main() -> None:
    host = g("HOME_SERVER")
    if not host:
        emit("--", "HOME_SERVER unset in globals.sh", "down")
        return
    label = g("HOME_SERVER_LABEL") or host.rsplit(".", 1)[-1]
    ok, rtt = ping_host(host, ipv6=False, timeout=1.5)
    mark = "●" if ok else "○"
    cls = "ok" if ok else "crit"
    tooltip = f"{host} {'up' if ok else 'down'}"
    if rtt:
        tooltip += f"  {rtt} ms"
    emit(f"{label}{mark}", tooltip, cls)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        emit("?", str(exc), "crit")
