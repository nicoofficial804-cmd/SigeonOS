#!/bin/bash
set -e

echo "=================================================="
echo "         SigeonOS Build Suite (HP Native Keys)    "
echo "=================================================="

echo "=== 1. Inizializzazione Portachiavi Pacman==="
pacman-key --init
pacman-key --populate archlinux

echo "=== 2. Aggiornamento Sistema e Installazione Dipendenze ==="
# NOTA: neofetch è stato rimosso dai repository, usiamo solo fastfetch
pacman -Syu --noconfirm archlinux-keyring archiso sbctl sbsigntools gdk-pixbuf2 mesa virtualbox-guest-utils-nox mpv ffmpeg fastfetch

echo "=== 3. Copia del Profilo Releng di Base ==="
rm -rf /root/archlive
cp -r /usr/share/archiso/configs/releng /root/archlive

echo "=== 4. Configurazione Schermata di Avvio (BIOS/Syslinux) ==="
if [ -f "/mnt/sigeon/boot_splash.png" ]; then
    echo "--> boot_splash.png personalizzata trovata! Iniezione nel bootloader..."
    mkdir -p /root/archlive/syslinux
    cp /mnt/sigeon/boot_splash.png /root/archlive/syslinux/splash.png
else
    echo "--> NOTA: boot_splash.png non trovata. Uso dello stile di default."
fi

echo "=== 5. Personalizzazione Etichette e Parametri di Boot ==="
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
    done
    add_file /opt/sigeon/boot.mp4
    add_runscript
}
help() {
    echo "Riproduce il video MP4 istantaneamente all'avvio del kernel come Plymouth"
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

echo "=== 6. Iniezione Dipendenze Grafiche e Multimediali ==="
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
fastfetch
python-pyqt6-webengine
EOF

echo "=== 7. Creazione Cartelle di Target ==="
mkdir -p /root/archlive/airootfs/opt/OS
mkdir -p /root/archlive/airootfs/root

echo "=== 8. Copia dell'Applicazione Principale OS (FIX CORRETTO) ==="
if [ -d "/mnt/sigeon/OS" ]; then
    echo "--> Copia del payload della directory OS..."
    # Uso -a con /. per copiare i file interni senza creare la cartella ricorsiva /opt/OS/OS
    cp -a /mnt/sigeon/OS/. /root/archlive/airootfs/opt/OS/
    chmod +x /root/archlive/airootfs/opt/OS/main.py
else
    echo "--> ERRORE CRITICO: La directory /mnt/sigeon/OS non esiste!"
    exit 1
fi

echo "=== 9. Scrittura Script di Inizializzazione Ambiente Grafico ==="
cat << 'EOF' > /root/archlive/airootfs/root/.xinitrc
export QT_QPA_PLATFORM=xcb
export DISPLAY=:0

echo "--> Avvio applicazione SigeonOS..."
python /opt/OS/main.py > /tmp/pyqt_stdout.log 2> /tmp/pyqt_error.log
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    poweroff
else
    echo $EXIT_CODE > /tmp/app_failed
fi
EOF

echo "=== 10. Configurazione Autostart al Login di Root ==="
cat << 'EOF' > /root/archlive/airootfs/root/.zlogin
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    rm -f /tmp/app_failed
    startx
    if [ -f /tmp/app_failed ]; then
        clear
        echo -e "\n\e[1;31m[!] SigeonOS crashed in a more fatal way than exptected. Error code : $(cat /tmp/app_failed).\e[0m"
        if [ -f /tmp/pyqt_error.log ]; then
            echo -e "\n\e[1;33m--- LOGS: ---\e[0m"
            cat /tmp/pyqt_error.log
            echo -e "\e[1;33m-----------------------------\e[0m"
        fi
        echo "Balling out: you are now in Arch Linux's TTY."
        fastfetch --config /etc/fastfetch/config.jsonc
    fi
fi
EOF

echo "=== 10b. CONFIGURAZIONE FASTFETCH E LOGO SIGEON ==="
mkdir -p /root/archlive/airootfs/usr/share/fastfetch/presets/
mkdir -p /root/archlive/airootfs/etc/fastfetch/

cat << 'EOF' > /root/archlive/airootfs/usr/share/fastfetch/presets/sigeon.txt
                          .=+***+=.            
                         -+**#=+***:           
                        :++++*##***#*+         
                        :++++++++*=            
                        -+++++++++.            
                        =+++++++**-            
                       :+++++++++*=            
                      .===+*##****+:           
                    :+*##*--##*+*##=           
                 .=*########%%%%%%#*.          
               .+*#########*#%%%%%%%:          
             -+*****#####***#%%%%%%%.          
            .=+************#%%%%%%%=           
            .+++++++++***+*%##%%%%-            
          -+++++++++++=-:=#####=:              
           .:::::..   .::..                    
EOF

cat << 'EOF' > /root/archlive/airootfs/etc/fastfetch/config.jsonc
{
    "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
    "logo": {
        "source": "/usr/share/fastfetch/presets/sigeon.txt",
        "color": { "1": "cyan" }
    },
    "modules": [
        { "type": "os", "key": "OS", "format": "SigeonOS" },
        "kernel",
        "uptime",
        "shell"
    ]
}
EOF

echo "=== 11. Generazione Chiavi di Firma Locali con sbctl ==="
if [ ! -d "/var/lib/sbctl/keys" ]; then
    echo "--> Creazione nuove chiavi di sicurezza UEFI..."
    sbctl create-keys
fi

echo "--> Generazione certificato sigeon-db.cer per il firmware HP..."
openssl x509 -in /var/lib/sbctl/keys/db/db.pem -outform DER -out /root/archlive/airootfs/root/sigeon-db.cer

mkdir -p /root/archlive/efiboot/EFI/HP/KEYS/
cp /root/archlive/airootfs/root/sigeon-db.cer /root/archlive/efiboot/EFI/HP/KEYS/db.cer

echo "=== 11b. Configurazione Permessi File in profiledef.sh ==="
cat << 'EOF' >> /root/archlive/profiledef.sh

# Definizioni di sicurezza e permessi aggiuntive per SigeonOS
file_permissions+=(
  ["/root/.xinitrc"]="0:0:0755"
  ["/root/.zlogin"]="0:0:0644"
  ["/root/.bash_profile"]="0:0:0644"
  ["/opt/OS/main.py"]="0:0:0755"
  ["/usr/share/fastfetch/presets/sigeon.txt"]="0:0:0644"
  ["/etc/fastfetch/config.jsonc"]="0:0:0644"
)
EOF

echo "=== 12. Creazione dell'Hook di Firma Interno ==="
mkdir -p /root/archlive/buildhooks
cat << 'EOF' > /root/archlive/buildhooks/sign_efi.sh
#!/bin/bash
echo "==> Build Hook: Firma nativa dei binari con sbsigntools..."
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

echo "=== 13. Avvio Compilazione Sincrona con mkarchiso ==="
mkdir -p /root/archiso-work
mkdir -p /root/archiso-out
rm -rf /root/archiso-work/*

# Copia degli hook personalizzati nelle directory di sistema dell'host prima che mkarchiso chiami mkinitcpio
mkdir -p /usr/lib/initcpio/hooks
mkdir -p /usr/lib/initcpio/install
cp /root/archlive/initcpio/hooks/sigeon_video /usr/lib/initcpio/hooks/sigeon_video
cp /root/archlive/initcpio/install/sigeon_video /usr/lib/initcpio/install/sigeon_video

mkarchiso -v -w /root/archiso-work -o /root/archiso-out /root/archlive

echo "=== 14. Trasferimento ISO Completata nello Workspace ==="
cp -v /root/archiso-out/*.iso /mnt/sigeon/

echo "=================================================="
echo "     ISO SIGEONOS GENERATA CON SUCCESSO!          "
echo "=================================================="