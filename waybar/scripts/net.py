#!/usr/bin/env python3
"""Physical NIC: compressed IPv6 + live negotiated speed. 100 Mbit warn once."""

from __future__ import annotations

import ipaddress
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ICON_GLOBE, cache_dir, emit, physical_ifaces, read_text, run  # noqa: E402

SPEED_FILE = cache_dir() / "link-speed"


def compress_v6(addr: str) -> str:
    try:
        c = ipaddress.IPv6Address(addr).compressed
    except ValueError:
        return addr
    if len(c) <= 22:
        return c
    parts = c.split(":")
    return f"{parts[0]}:{parts[1]}:…:{parts[-1]}"


def ip_json() -> dict:
    try:
        proc = run(["ip", "-j", "addr"], timeout=2)
        addrs = json.loads(proc.stdout) if proc.returncode == 0 else []
    except (json.JSONDecodeError, subprocess.TimeoutExpired):
        addrs = []
    try:
        proc = run(["ip", "-j", "route"], timeout=2)
        routes = json.loads(proc.stdout) if proc.returncode == 0 else []
    except (json.JSONDecodeError, subprocess.TimeoutExpired):
        routes = []
    return {"addr": addrs, "route": routes}


def pick_iface(data: dict) -> str | None:
    names = physical_ifaces()
    # Prefer carrier-up ethernet/wifi
    for name in names:
        oper = read_text(f"/sys/class/net/{name}/operstate")
        if oper == "up":
            return name
    return names[0] if names else None


def addrs_for(iface: str, data: dict) -> tuple[str | None, str | None, str | None]:
    v4 = v6 = cidr4 = None
    for link in data.get("addr") or []:
        if link.get("ifname") != iface:
            continue
        for a in link.get("addr_info") or []:
            fam = a.get("family")
            local = a.get("local")
            prefix = a.get("prefixlen")
            scope = a.get("scope")
            if not local:
                continue
            if fam == "inet" and v4 is None:
                v4 = local
                cidr4 = f"{local}/{prefix}"
            elif fam == "inet6" and scope == "global" and v6 is None:
                v6 = local
    return v4, v6, cidr4


def gateway(iface: str, data: dict) -> str | None:
    for r in data.get("route") or []:
        if r.get("dst") == "default" and r.get("dev") == iface:
            return r.get("gateway")
    for r in data.get("route") or []:
        if r.get("dst") == "default" and r.get("gateway"):
            return r.get("gateway")
    return None


def format_speed(raw: str | None, kind: str) -> str:
    if kind == "wifi":
        return "Wi-Fi"
    try:
        mb = int(raw or "0")
    except ValueError:
        return "?"
    if mb <= 0:
        return "?"
    if mb >= 1000 and mb % 1000 == 0:
        return f"{mb // 1000}G"
    return f"{mb}M"


def notify_100(iface: str, speed: int, prev: str | None) -> None:
    prev_s = prev if prev is not None else ""
    if speed == 100 and prev_s != "100":
        run(
            [
                "notify-send",
                "-u",
                "critical",
                "-i",
                "network-error",
                "Link 100 Mbit",
                f"{iface} negotiated 100 Mbit",
            ],
            timeout=2,
        )


def main() -> None:
    data = ip_json()
    iface = pick_iface(data)
    if not iface:
        emit(f"{ICON_GLOBE} no-link", "no physical interface", "down")
        return

    oper = read_text(f"/sys/class/net/{iface}/operstate") or "down"
    carrier = read_text(f"/sys/class/net/{iface}/carrier") or "0"
    speed_raw = read_text(f"/sys/class/net/{iface}/speed")
    kind = "wifi" if Path(f"/sys/class/net/{iface}/wireless").exists() else "eth"
    duplex = read_text(f"/sys/class/net/{iface}/duplex") or "?"

    v4, v6, cidr4 = addrs_for(iface, data)
    gw = gateway(iface, data)
    speed_label = format_speed(speed_raw, kind)

    try:
        speed_i = int(speed_raw) if speed_raw and speed_raw.lstrip("-").isdigit() else 0
    except ValueError:
        speed_i = 0

    prev = read_text(SPEED_FILE)
    if oper == "up" and carrier == "1" and speed_i > 0:
        notify_100(iface, speed_i, prev)
        SPEED_FILE.write_text(str(speed_i))
    elif oper != "up":
        SPEED_FILE.write_text("down")

    compact = compress_v6(v6) if v6 else (v4 or "no-ip")
    text = f"{ICON_GLOBE} {compact} {speed_label}"

    cls = "ok"
    if oper != "up" or carrier != "1":
        cls = "down"
        text = f"{ICON_GLOBE} {iface} down"
    elif kind == "eth" and speed_i == 100:
        cls = "warn-100"

    tooltip = "\n".join(
        [
            f"{iface} {'wifi' if kind == 'wifi' else 'ethernet'}",
            f"state: {oper}  carrier: {carrier}",
            f"v6: {v6 or 'none'}",
            f"v4: {cidr4 or v4 or 'none'}",
            f"gw: {gw or 'none'}",
            f"speed: {speed_raw or '?'} Mb/s {duplex}",
        ]
    )
    emit(text, tooltip, cls)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        emit(f"{ICON_GLOBE} --", str(exc), "down")
