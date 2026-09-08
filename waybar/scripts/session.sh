#!/bin/sh
# Confirm session action in fuzzel. Logout returns to ly. Never a one-pixel hit.
set -eu

choice=$(printf '%s\n' Cancel Suspend Logout | fuzzel --dmenu --prompt 'session> ' --width 24 --lines 3 || true)
case "${choice:-}" in
	Logout)
		exec loginctl terminate-session "${XDG_SESSION_ID:-}"
		;;
	Suspend)
		exec systemctl suspend
		;;
	*)
		exit 0
		;;
esac
