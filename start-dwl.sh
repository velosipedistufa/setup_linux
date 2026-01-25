#!/bin/sh
#export XDG_SESSION_TYYPE=wayland
export XDG_SESSION_TYPE=wayland
export XDG_CURRENT_DESKTOP=dwl
export XDG_SESSION_DESKTOP=dwl
export MOZ_ENABLE_WAYLAND=1
export SDL_VIDEODRIVER=wayland
export _JAVA_AWT_WM_NONREPARENTING=1
#while [ ! -S /run/user$(id -u)/wayland-0 ]; do
#	sleep 0.1
#done
/usr/lib/xdg-desktop-portal-wlr &
/home/alex/appearance/dwl/dwl & 
sleep 1
waybar &
swaybg -i ~/appearance/wallpaper.png -m fit -o*
#/usr/lib/xdg-desktop-portal-wlr &
exec udiskie -A -n &
#sleep 1000
#/usr/lib/xdg-desktop-portal-wlr &
#exec dwl
