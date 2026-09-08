#!/bin/sh
# Toggle mihomo-tui in kitty. Never touch the mihomo daemon.
set -eu

if pgrep -x mihomo-tui >/dev/null 2>&1; then
	pkill -x mihomo-tui || true
	pkill -f 'mihomo-tui-launch' || true
	exit 0
fi

exec kitty --class mihomo-tui -e "$HOME/.local/bin/mihomo-tui-launch"
