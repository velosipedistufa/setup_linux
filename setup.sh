#!/bin/bash
set -euo pipefail
# Create user if missing
mkdir -p /usr/share/wayland-sessions
runuser -u alex mkdir /home/alex/appearance/
runuser -u alex scp alex@192.168.88.1:/home/alex/apearance/archiv.7z /home/alex/appearance
runuser -u alex 7z x archiv.7z
sudo cp -a /home/alex/appearance/wayland-sessions/. /usr/share/wayland-sessions/
sudo cp -a /home/alex/appearance/waybar/. /etc/xdg/waybar
pacman -Syu --noconfirm fuzzel ffmpeg swaybg waybar pipewire wireplumber wayland libinput pkg-config pipewire-jack git cmatrix btop htop go udiskie xdg-desktop-portal xdg-desktop-portal-wlr kitty thunar mousepad playerctl bluez bluez-utils jq libxss mailcap libxt gnu-free-fonts lxappearance gtk4 pipewire-alsa pipewire-v4l2 sof-firmware alsa-ucm-conf grim slurp wl-clipboard swappy gvfs 7zip neovim hyfetch
#pipewire-alsa should be removed as far as firefox will implement pipewire support
runuser -u alex git clone https://aur.archlinux.org/yay.git
cd yay
runuser -u alex makepkg -si
cd ..
runuser -u alex yay -S --sudoloop wlroots0.19 wayland-protocols ly flat-remix #vimix-gtk-theme

cd appearance

runuser -u alex git clone https://codeberg.org/dwl/dwl

cp /home/alex/appearance/dwl/config.h /home/alex/appearance/dwl
runuser -u alex  make
#./dwl
#systemctl enable ly@service #ly@.service outputs Failed to enable unit: Refusing to operate on template unit ly@.service when destination unit multi-user.target is a non-template unit, on both vm and host
systemctl enable ly@tty2.service
systemctl disable getty@tty2.service

#cp start-dwl.sh /home/alex/appearance
#cp config.h /home/alex/dwl/
#cp wallpaper.png /home/alex/appearance

#sudo pacman -S firefox libreoffice
echo "we're done"



#below is test field, if some command will help
systemctl --user enable --now pipewire wireplumber
