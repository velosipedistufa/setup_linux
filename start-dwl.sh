#!/bin/sh
export XDG_SESSION_TYPE=wayland
export XDG_CURRENT_DESKTOP=dwl
export XDG_SESSION_DESKTOP=dwl
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export MOZ_ENABLE_WAYLAND=1
export GDK_BACKEND=wayland
export QT_QPA_PLATFORM=wayland
export CLUTTER_BACKEND=wayland
export SDL_VIDEODRIVER=wayland
export ELECTRON_OZONE_PLATFORM_HINT=wayland
export _JAVA_AWT_WM_NONREPARENTING=1

G="${HOME}/.config/setup_linux/globals.sh"
[ -f "$G" ] && . "$G"

/usr/lib/xdg-desktop-portal-wlr &
DW="${HOME}/appearance/dwl/dwl"
[ -x "$DW" ] && "$DW" &

# Wait for the compositor's Wayland socket, not X11.
for i in $(seq 1 50); do
	[ -S "${XDG_RUNTIME_DIR}/wayland-0" ] && break
	sleep 0.1
done

pgrep -x mako >/dev/null 2>&1 || mako &
if [ -n "${KEYBOARD_EVENT:-}" ] && [ -r "${KEYBOARD_EVENT}" ]; then
	pgrep -x layout-watch >/dev/null 2>&1 || "$HOME/.config/waybar/scripts/layout-watch" "$KEYBOARD_EVENT" &
fi
waybar &
swaybg -i "$HOME/appearance/wallpaper.png" -m fit -o*
exec udiskie -A -n &
