# Copy to globals.sh and edit. globals.sh is gitignored — do not commit it.
#   cp globals.example.sh globals.sh
#
# Install scripts:  . ./globals.sh
# Waybar: reads the same file (or ~/.config/setup_linux/globals.sh after setup.sh).

# Login user created by archinstall2.sh / used by setup.sh
USER_NAME=alex
USER_PASSWORD=123
HOSTNAME=arch

# Whole-disk device. nvme/mmcblk get p1/p2; sda/vda get 1/2.
# Examples: /dev/nvme0n1   /dev/sda   /dev/vda
DISK=/dev/nvme0n1

# LAN host to ping on the bar (home server). Short label is the plate text.
HOME_SERVER=192.168.88.6
HOME_SERVER_LABEL=88.6
# Optional. Empty = derive x.y.z.255 from HOME_SERVER.
LAN_BCAST=

# Remote VPS: DNS name plus the A / AAAA you expect. Bar checks DoH matches
# these addresses, then pings the addresses (not the name — avoids fake-ip).
VPS_HOST=bashirov.org
VPS_A=185.189.149.245
VPS_AAAA=2a0b:7140:4:1:5054:ff:fea2:2498
VPS_LABEL=VPS

# Keyboard evdev for layout-watch (display only). Empty = skip watcher.
KEYBOARD_EVENT=/dev/input/event4
# udev ATTRS{uniq} so the user can read that node after replug. Empty = skip rule.
KEYBOARD_UNIQ=7870E6CACAA1E4F6

# Shown next to memory / VRAM on the bar.
RAM_TYPE=DDR3
VRAM_TYPE=GDDR5
