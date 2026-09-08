#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
#loadkeys colemak
#cat /sys/firmware/efi/fw_platform_size
#ping -c 4 8.8.8.8
if [ ! -f "$HERE/globals.sh" ]; then
	echo "copy globals.example.sh to globals.sh and edit DISK / USER_NAME / passwords" >&2
	exit 1
fi
# shellcheck disable=SC1091
. "$HERE/globals.sh"

disk_part() {
	case "$DISK" in
		*nvme*|*mmcblk*|*loop*|*nbd*) echo "${DISK}p$1" ;;
		*) echo "${DISK}$1" ;;
	esac
}

cd
sgdisk --zap-all "$DISK"
sgdisk \
  -n 1:0:+1G   -t 1:ef00 -c 1:"EFI System" \
  -n 2:0:0     -t 2:8300 -c 2:"Linux root" \
  "$DISK"
partprobe "$DISK"

EFI="$(disk_part 1)"
ROOT="$(disk_part 2)"

#cfdisk "$DISK" #(1G EFI system, Then the rest is Linux root (x86_64)) maybe arm one day...

mkfs.ext4 "$ROOT"
mkfs.fat -F 32 "$EFI"

mount "$ROOT" /mnt
mount --mkdir "$EFI" /mnt/boot
 timedatectl set-ntp true
 pacman-key --init
 pacman-key --populate archlinux
 pacman -Sy --noconfirm archlinux-keyring
#mkdir -p /mnt/root
#cp -v /root/archinstall.sh /mnt/root/archinstall.sh
#chmod +x /mnt/root/archinstall.sh

#pacstrap -K /mnt base base-devel linux linux-firmware linux-headers networkmanager network-manager-applet wpa_supplicant wireless_tools dialog mtools dosfstools nano vim
pacstrap -K /mnt base base-devel linux linux-firmware networkmanager network-manager-applet wpa_supplicant wireless_tools dialog mtools dosfstools nano vim
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt
#arch-chroot /mnt /bin/bash -eux <<'CHROOT'
