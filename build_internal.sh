#!/bin/bash
set -e

echo "=================================================="
echo "                  SigeonOS Builder   "
echo "=================================================="
pacman-key --init
pacman-key --populate archlinux
pacman -Syu --noconfirm archlinux-keyring archiso sbctl sbsigntools gdk-pixbuf2 mesa virtualbox-guest-utils-nox mpv ffmpeg
rm -rf /root/archlive
cp -r /usr/share/archiso/configs/releng /root/archlive
if [ -f "/mnt/sigeon/boot_splash.png" ]; then
    echo "--> boot_splash.png found! Injecting in ISO"
    mkdir -p /root/archlive/syslinux
    cp /mnt/sigeon/boot_splash.png /root/archlive/syslinux/splash.png
else
    echo "--> WARNING: boot_splash.png not found, using original"
fi
BOOT_PARAMS="quiet loglevel=0 systemd.show_status=false rd.systemd.show_status=false rd.udev.log_level=0 vt.global_cursor_default=0 udev.log_priority=0"

if [ -d "/root/archlive/syslinux" ]; then
    find /root/archlive/syslinux/ -type f -name "*.cfg" -exec sed -i \
        -e 's/Arch Linux/SigeonOS/g' \
        -e 's/install medium/Boot/g' \
        -e "s/archisobabel=%ARCHISO_LABEL%/archisobabel=%ARCHISO_LABEL% ${BOOT_PARAMS}/g" {} +
fi

if [ -d "/root/archlive/efiboot/loader/entries" ]; then
    find /root/archlive/efiboot/loader/entries/ -type f -name "*.conf" -exec sed -i \
        -e 's/Arch Linux/SigeonOS/g' \
        -e "s/archisobabel=%ARCHISO_LABEL%/archisobabel=%ARCHISO_LABEL% ${BOOT_PARAMS}/g" {} +
fi

echo "=== 5b. CONFIGURAZIONE EARLY VIDEO IN INITRAMFS (Stile Plymouth) ==="
mkdir -p /root/archlive/initcpio/hooks
mkdir -p /root/archlive/initcpio/install
cat << 'EOF' > /root/archlive/initcpio/install/sigeon_video
#!/bin/bash

build() {
    add_binary /usr/bin/mpv
    for lib in $(ldd /usr/bin/mpv | grep "=> /" | awk '{print $3}'); do
        add_file "$lib"
    donee
    add_file /opt/sigeon/boot.mp4
    add_runscript
}

help() {
    echo "DEPRECATED / NOT WORKING : starts video for boot like plymouth"
}
EOF
cat << 'EOF' > /root/archlive/initcpio/hooks/sigeon_video
#!/usr/bin/ash

run_hook() {
    echo "--> SigeonOS Early Boot Video..."
    /usr/bin/mpv --vo=drm --quiet --no-osc --no-osd-bar --keep-open=no /opt/sigeon/boot.mp4
}
EOF
mkdir -p /root/archlive/airootfs/opt/sigeon
if [ -f "/mnt/sigeon/splash_video/boot.mp4" ]; then
    cp /mnt/sigeon/splash_video/boot.mp4 /root/archlive/airootfs/opt/sigeon/boot.mp4
else
    ffmpeg -f lavfi -i color=c=black:s=1280:720:d=1 /root/archlive/airootfs/opt/sigeon/boot.mp4
fi
cat << 'EOF' > /root/archlive/mkinitcpio.conf
MODULES=(vboxvideo virtio_gpu nouveaudrm radeon i915)
BINARIES=()
FILES=(/opt/sigeon/boot.mp4)
HOOKS=(base udev sigeon_video memdisk archiso_loop_mnt archiso archiso_pxe_common archiso_pxe_nbd archiso_pxe_http archiso_pxe_nfs archiso_vfat late_modules)
COMPRESSION="xz"
EOF

sed -i 's/mkinitcpio_conf="mkinitcpio.conf"/mkinitcpio_conf="mkinitcpio.conf"/g' /root/archlive/profiledef.sh
cat << 'EOF' >> /root/archlive/packages.x86_64
python
xorg-server
xorg-xinit
libxkbcommon-x11
ttf-dejavu
python-pyqt6
qt6-multimedia
gst-plugins-good
alsa-utils
gdk-pixbuf2
virtualbox-guest-utils-nox
mesa
mpv
EOF
mkdir -p /root/archlive/airootfs/opt
mkdir -p /root/archlive/airootfs/root
if [ -d "/mnt/sigeon/OS" ]; then
    echo "--> Copia del payload della directory OS..."
    cp -r /mnt/sigeon/OS /root/archlive/airootfs/opt/OS
    chmod +x /root/archlive/airootfs/opt/OS/main.py
else
    echo "--> ERROR: /mnt/sigeon/OS does not exist!"
    exit 1
fi
cat << 'EOF' > /root/archlive/airootfs/root/.xinitrc
export QT_QPA_PLATFORM=xcb
export DISPLAY=:0
python /opt/OS/main.py > /tmp/pyqt_stdout.log 2> /tmp/pyqt_error.log
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    poweroff
else
    echo $EXIT_CODE > /tmp/app_failed
fi
EOF
cat << 'EOF' > /root/archlive/airootfs/root/.zlogin
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    rm -f /tmp/app_failed
    startx
    if [ -f /tmp/app_failed ]; then
        echo -e "\n\e[1;31m[!] SigeonOS crashed with error code $(cat /tmp/app_failed).\e[0m"
        if [ -f /tmp/pyqt_error.log ]; then
            echo -e "\n\e[1;33m--- LOG FOR DEBUGGING: ---\e[0m"
            cat /tmp/pyqt_error.log
            echo -e "\e[1;33m-----------------------------\e[0m"
        fi
        echo "If you keep seeing this message, then your OS may be corrupted."
        echo "You are now in Arch Linux TTY."
    fi
fi
EOF

cat << 'EOF' > /root/archlive/airootfs/root/.bash_profile
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    rm -f /tmp/app_failed
    startx
    if [ -f /tmp/app_failed ]; then
        echo -e "\n\e[1;31m[!] SigeonOS crashed with error code $(cat /tmp/app_failed).\e[0m"
        if [ -f /tmp/pyqt_error.log ]; then
            echo -e "\n\e[1;33m--- LOG FOR DEBUGGING: ---\e[0m"
            cat /tmp/pyqt_error.log
            echo -e "\e[1;33m-----------------------------\e[0m"
        fi
        echo "If you keep seeing this message, then your OS may be corrupted."
        echo "You are now in Arch Linux TTY."
    fi
fi
EOF
if [ ! -d "/var/lib/sbctl/keys" ]; then
    sbctl create-keys
fi

openssl x509 -in /var/lib/sbctl/keys/db/db.pem -outform DER -out /root/archlive/airootfs/root/sigeon-db.cer

mkdir -p /root/archlive/efiboot/EFI/HP/KEYS/
cp /root/archlive/airootfs/root/sigeon-db.cer /root/archlive/efiboot/EFI/HP/KEYS/db.cer

cat << 'EOF' >> /root/archlive/profiledef.sh

file_permissions+=(
  ["/root/.xinitrc"]="0:0:0755"
  ["/root/.zlogin"]="0:0:0644"
  ["/root/.bash_profile"]="0:0:0644"
  ["/opt/OS/main.py"]="0:0:0755"
)
EOF

mkdir -p /root/archlive/buildhooks
cat << 'EOF' > /root/archlive/buildhooks/sign_efi.sh
#!/bin/bash
KEY="/var/lib/sbctl/keys/db/db.key"
CERT="/var/lib/sbctl/keys/db/db.pem"

find "$work_dir/efiboot" -type f -name "*.efi" -exec sbsign --key "$KEY" --cert "$CERT" --output {} {} \; 2>/dev/null || true
find "$work_dir/iso/EFI" -type f -name "*.efi" -exec sbsign --key "$KEY" --cert "$CERT" --output {} {} \; 2>/dev/null || true
if [ -f "$work_dir/iso/boot/vmlinuz-linux" ]; then
    sbsign --key "$KEY" --cert "$CERT" --output "$work_dir/iso/boot/vmlinuz-linux" "$work_dir/iso/boot/vmlinuz-linux"
fi
EOF
chmod +x /root/archlive/buildhooks/sign_efi.sh
echo "build_hooks+=('/root/archlive/buildhooks/sign_efi.sh')" >> /root/archlive/profiledef.sh
mkdir -p /root/archiso-work
mkdir -p /root/archiso-out
rm -rf /root/archiso-work/*

mkdir -p /usr/lib/initcpio/hooks
mkdir -p /usr/lib/initcpio/install
cp /root/archlive/initcpio/hooks/sigeon_video /usr/lib/initcpio/hooks/sigeon_video
cp /root/archlive/initcpio/install/sigeon_video /usr/lib/initcpio/install/sigeon_video

mkarchiso -v -w /root/archiso-work -o /root/archiso-out /root/archlive

echo "=== 14. Trasferimento ISO Completata nello Workspace ==="
cp -v /root/archiso-out/*.iso /mnt/sigeon/

echo "=================================================="
echo "              COMPILED ISO WITH SUCCESS!          "
echo "=================================================="