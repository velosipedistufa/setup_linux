#loadkeys colemak
#cat /sys/firmware/efi/fw_platform_size
#ping -c 4 8.8.8.8
cd
DISK=/dev/nvme0n1
sgdisk --zap-all "$DISK"
sgdisk \
  -n 1:0:+1G   -t 1:ef00 -c 1:"EFI System" \
  -n 2:0:0     -t 2:8300 -c 2:"Linux root" \
  "$DISK"
partprobe "$DISK"


#cfdisk /dev/$DISK #(1G EFI system, Then the rest is Linux root (x86_64)) maybe arm one day...

mkfs.ext4 $DISK'p2'
mkfs.fat -F 32 $DISK'p1'

mount $DISK'p2' /mnt
mount --mkdir $DISK'p1' /mnt/boot
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

