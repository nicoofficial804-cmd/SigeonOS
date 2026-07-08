import sys
import os
import shutil
import platform
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QListWidget, QListWidgetItem, QStackedWidget,
                             QFrame, QProgressBar, QGridLayout, QScrollArea, QSlider,
                             QInputDialog, QMessageBox, QComboBox, QCheckBox)
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl
from PyQt6.QtGui import QIcon, QColor, QPixmap
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import theme
import apps.users as users_helper

class SigeonSettings(QWidget):
    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.volume = 50
        self.bluetooth_enabled = True
        self.wifi_enabled = True
        self.connected_network = "NestLink_5G"
        
        # Audio feedback player
        self.audio_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.audio_player.setAudioOutput(self.audio_output)
        boot_audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "boot.mp3")
        if os.path.exists(boot_audio_path):
            self.audio_player.setSource(QUrl.fromLocalFile(boot_audio_path))
            
        self.init_ui()

    def init_ui(self):
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 1. Left Sidebar
        self.sidebar = QWidget(self)
        self.sidebar.setObjectName("settings_sidebar")
        self.sidebar.setFixedWidth(190)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 12, 0, 12)
        
        # Header profile
        self.profile_widget = QWidget(self.sidebar)
        self.profile_layout = QHBoxLayout(self.profile_widget)
        self.profile_layout.setContentsMargins(12, 0, 12, 12)
        
        self.profile_pic = QLabel(self.profile_widget)
        self.profile_pic.setPixmap(theme.IconFactory.get_icon("logo_white", 28).pixmap(28, 28))
        self.profile_pic.setStyleSheet("background-color: rgba(255,255,255,0.15); border-radius: 14px; padding: 2px;")
        self.profile_layout.addWidget(self.profile_pic)
        
        self.profile_text = QWidget(self.profile_widget)
        self.pt_layout = QVBoxLayout(self.profile_text)
        self.pt_layout.setContentsMargins(0, 0, 0, 0)
        self.pt_layout.setSpacing(0)
        
        current_username = "Sky Pigeon"
        if self.desktop and self.desktop.main_window and self.desktop.main_window.fs:
            current_username = self.desktop.main_window.fs.current_user or "Sky Pigeon"
            
        self.profile_name = QLabel(current_username, self.profile_text)
        self.profile_name.setStyleSheet("font-weight: bold; font-size: 11px; color: #1a1f26;")
        self.profile_email = QLabel(f"{current_username.lower().replace(' ', '')}@pigeon.os", self.profile_text)
        self.profile_email.setStyleSheet("font-size: 9px; color: #7f8c8d;")
        self.pt_layout.addWidget(self.profile_name)
        self.pt_layout.addWidget(self.profile_email)
        self.profile_layout.addWidget(self.profile_text)
        self.profile_layout.addStretch()
        
        self.sidebar_layout.addWidget(self.profile_widget)
        
        # Sidebar Menu
        self.menu_list = QListWidget(self.sidebar)
        self.menu_list.setObjectName("settings_sidebar_list")
        self.menu_list.currentRowChanged.connect(self.menu_changed)
        
        self.add_menu_item("System", "settings")
        self.add_menu_item("Bluetooth & Devices", "wing_drive")
        self.add_menu_item("Network & Internet", "cloud_nest")
        self.add_menu_item("Personalization", "photos")
        self.add_menu_item("Accounts", "logo")
        self.add_menu_item("Power & Battery", "recycle_empty")
        self.add_menu_item("About Sigeon OS", "logo_white")
        
        self.sidebar_layout.addWidget(self.menu_list)
        self.layout.addWidget(self.sidebar)
        
        # 2. Right Stacked Widget
        self.stack = QStackedWidget(self)
        self.layout.addWidget(self.stack, stretch=1)
        
        # Initialize pages
        self.create_system_page()
        self.create_bluetooth_page()
        self.create_network_page()
        self.create_personalization_page()
        self.create_accounts_page()
        self.create_power_page()
        self.create_about_page()
        
        self.menu_list.setCurrentRow(0)

    def add_menu_item(self, name, icon_name):
        item = QListWidgetItem(name)
        item.setIcon(theme.IconFactory.get_icon(icon_name, 16))
        self.menu_list.addItem(item)

    def menu_changed(self, index):
        self.stack.setCurrentIndex(index)

    # ================= PAGE 1: System Page (Display, Sound, Storage) =================
    def create_system_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(20, 20, 20, 20)
        page_layout.setSpacing(15)
        
        title = QLabel("System Settings", page)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26;")
        page_layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(12)
        
        # 1. DISPLAY SECTION
        display_box = QFrame()
        display_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        disp_lay = QVBoxLayout(display_box)
        disp_lay.setContentsMargins(15, 12, 15, 12)
        
        disp_hdr = QLabel("Display")
        disp_hdr.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        disp_lay.addWidget(disp_hdr)
        
        # Brightness Slider
        bright_lay = QHBoxLayout()
        bright_lbl = QLabel("Screen Brightness:")
        bright_lbl.setStyleSheet("font-size: 11px; color: #2c3e50;")
        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(20, 100)
        self.bright_slider.setValue(100)
        self.bright_slider.valueChanged.connect(self.update_brightness)
        self.bright_val_lbl = QLabel("100%")
        self.bright_val_lbl.setFixedWidth(30)
        self.bright_val_lbl.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        
        bright_lay.addWidget(bright_lbl)
        bright_lay.addWidget(self.bright_slider, stretch=1)
        bright_lay.addWidget(self.bright_val_lbl)
        disp_lay.addLayout(bright_lay)
        
        # Night Light Toggle
        nl_lay = QHBoxLayout()
        nl_lbl = QLabel("Night Light (Warm Filter):")
        nl_lbl.setStyleSheet("font-size: 11px; color: #2c3e50;")
        self.nl_chk = QCheckBox()
        self.nl_chk.stateChanged.connect(self.update_night_light)
        
        nl_lay.addWidget(nl_lbl)
        nl_lay.addWidget(self.nl_chk)
        nl_lay.addStretch()
        disp_lay.addLayout(nl_lay)
        scroll_layout.addWidget(display_box)
        
        # 2. SOUND SECTION
        sound_box = QFrame()
        sound_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        sound_lay = QVBoxLayout(sound_box)
        sound_lay.setContentsMargins(15, 12, 15, 12)
        
        sound_hdr = QLabel("Sound")
        sound_hdr.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        sound_lay.addWidget(sound_hdr)
        
        vol_lay = QHBoxLayout()
        self.vol_icon = QLabel("🔊")
        self.vol_icon.setStyleSheet("font-size: 14px;")
        
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        self.vol_slider.valueChanged.connect(self.update_volume)
        self.vol_slider.sliderReleased.connect(self.play_sound_feedback)
        
        self.vol_val_lbl = QLabel("50%")
        self.vol_val_lbl.setFixedWidth(30)
        self.vol_val_lbl.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        
        vol_lay.addWidget(self.vol_icon)
        vol_lay.addWidget(self.vol_slider, stretch=1)
        vol_lay.addWidget(self.vol_val_lbl)
        sound_lay.addLayout(vol_lay)
        scroll_layout.addWidget(sound_box)
        
        # 3. STORAGE SECTION
        storage_box = QFrame()
        storage_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        storage_lay = QVBoxLayout(storage_box)
        storage_lay.setContentsMargins(15, 12, 15, 12)
        
        storage_hdr = QLabel("Storage")
        storage_hdr.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        storage_lay.addWidget(storage_hdr)
        
        # Read real host disk usage
        total, used, free = shutil.disk_usage(".")
        total_gb = total / (1024 ** 3)
        used_gb = used / (1024 ** 3)
        free_gb = free / (1024 ** 3)
        usage_pct = int((used / total) * 100)
        
        storage_info = QLabel(f"Local Disk (C:) - {usage_pct}% Used")
        storage_info.setStyleSheet("font-size: 11px; font-weight: bold; color: #2c3e50;")
        storage_lay.addWidget(storage_info)
        
        self.storage_progress = QProgressBar()
        self.storage_progress.setValue(usage_pct)
        self.storage_progress.setFixedHeight(12)
        self.storage_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 4px;
                background-color: #f1f2f6;
                text-align: center;
                font-size: 8px;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #0f82df;
                border-radius: 3px;
            }
        """)
        storage_lay.addWidget(self.storage_progress)
        
        details_lbl = QLabel(f"Used space: {used_gb:.1f} GB &nbsp;&nbsp;|&nbsp;&nbsp; Free space: {free_gb:.1f} GB &nbsp;&nbsp;|&nbsp;&nbsp; Total size: {total_gb:.1f} GB")
        details_lbl.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        storage_lay.addWidget(details_lbl)
        
        scroll_layout.addWidget(storage_box)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        page_layout.addWidget(scroll)
        self.stack.addWidget(page)

    def update_brightness(self, value):
        self.bright_val_lbl.setText(f"{value}%")
        main_win = self.desktop.main_window if self.desktop else None
        if main_win and hasattr(main_win, 'display_overlay') and main_win.display_overlay:
            main_win.display_overlay.set_brightness(value)

    def update_night_light(self, state):
        enabled = (state == 2)
        main_win = self.desktop.main_window if self.desktop else None
        if main_win and hasattr(main_win, 'display_overlay') and main_win.display_overlay:
            main_win.display_overlay.set_night_light(enabled)

    def update_volume(self, value):
        self.volume = value
        self.vol_val_lbl.setText(f"{value}%")
        if value == 0:
            self.vol_icon.setText("🔇")
        elif value < 33:
            self.vol_icon.setText("🔈")
        elif value < 66:
            self.vol_icon.setText("🔉")
        else:
            self.vol_icon.setText("🔊")
            
        self.audio_output.setVolume(value / 100.0)

    def play_sound_feedback(self):
        try:
            self.audio_player.setPosition(0)
            self.audio_player.play()
        except:
            pass

    # ================= PAGE 2: Bluetooth & Devices Page =================
    def create_bluetooth_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Bluetooth & Devices", page)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26;")
        layout.addWidget(title)
        
        # BT Enable Box
        enable_box = QFrame()
        enable_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        enable_lay = QHBoxLayout(enable_box)
        
        bt_lbl = QLabel("Bluetooth Radio State")
        bt_lbl.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        enable_lay.addWidget(bt_lbl)
        enable_lay.addStretch()
        
        self.bt_toggle = QPushButton("ON")
        self.bt_toggle.setFixedSize(50, 24)
        self.bt_toggle.setStyleSheet("background-color: #2ec27e; color: white; border-radius: 4px; font-weight: bold;")
        self.bt_toggle.clicked.connect(self.toggle_bluetooth)
        enable_lay.addWidget(self.bt_toggle)
        layout.addWidget(enable_box)
        
        # Devices list
        dev_title = QLabel("Connected & Paired Devices:")
        dev_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(dev_title)
        
        self.devices_scroll = QScrollArea()
        self.devices_scroll.setWidgetResizable(True)
        self.devices_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.devices_widget = QWidget()
        self.dev_list_layout = QVBoxLayout(self.devices_widget)
        self.dev_list_layout.setContentsMargins(0, 0, 10, 0)
        self.dev_list_layout.setSpacing(8)
        
        self.bt_devices = [("Loading devices...", "Please wait", "")]
        self.refresh_bluetooth_list()
        
        QTimer.singleShot(100, self.async_load_bluetooth)
        
        self.devices_scroll.setWidget(self.devices_widget)
        layout.addWidget(self.devices_scroll)
        
        # Add device button
        self.btn_add_bt = QPushButton("Pair new device")
        self.btn_add_bt.setObjectName("settings_primary_btn")
        self.btn_add_bt.setStyleSheet(theme.get_stylesheet())
        self.btn_add_bt.clicked.connect(self.pair_bluetooth_action)
        layout.addWidget(self.btn_add_bt)
        
        self.stack.addWidget(page)

    def toggle_bluetooth(self):
        self.bluetooth_enabled = not self.bluetooth_enabled
        if self.bluetooth_enabled:
            self.bt_toggle.setText("ON")
            self.bt_toggle.setStyleSheet("background-color: #2ec27e; color: white; border-radius: 4px; font-weight: bold;")
            self.devices_scroll.setEnabled(True)
            self.btn_add_bt.setEnabled(True)
        else:
            self.bt_toggle.setText("OFF")
            self.bt_toggle.setStyleSheet("background-color: #7f8c8d; color: white; border-radius: 4px; font-weight: bold;")
            self.devices_scroll.setEnabled(False)
            self.btn_add_bt.setEnabled(False)

    def fetch_real_bt_devices(self):
        import subprocess, sys
        devices = []
        try:
            if sys.platform.startswith("linux"):
                res = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True, timeout=2)
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        parts = line.split(" ", 2)
                        if len(parts) >= 3:
                            name = parts[2]
                            devices.append((name, "Bluetooth Device", "Paired"))
            elif sys.platform == "win32":
                cmd = 'Get-PnpDevice -Class Bluetooth | Select-Object -Property FriendlyName, Status | ConvertTo-Json'
                res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    import json
                    try:
                        data = json.loads(res.stdout)
                        if isinstance(data, dict): data = [data]
                        
                        seen_names = set()
                        ignore_words = ["Servizio", "Profilo", "Enumeratore", "Microsoft", "MediaTek", "Bluetooth Device", "Trasporto"]
                        
                        for item in data:
                            name = item.get("FriendlyName")
                            status = item.get("Status")
                            
                            if status == "OK" and name and name not in seen_names:
                                if not any(word.lower() in name.lower() for word in ignore_words):
                                    devices.append((name, "Bluetooth Device", "Paired"))
                                    seen_names.add(name)
                    except Exception:
                        pass
        except Exception:
            pass
            
        if not devices:
            devices = [
                ("PigeonBuds Pro", "Audio device", "Connected"),
                ("WingMouse 2", "Pointer device", "Connected"),
                ("CooKeyboard", "Keyboard", "Paired")
            ]
        return devices

    def async_load_bluetooth(self):
        self.bt_devices = self.fetch_real_bt_devices()
        self.refresh_bluetooth_list()

    def refresh_bluetooth_list(self):
        # Clear layout
        while self.dev_list_layout.count():
            item = self.dev_list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
                
        for name, kind, status in self.bt_devices:
            card = QFrame()
            card.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
            card_lay = QHBoxLayout(card)
            card_lay.setContentsMargins(12, 8, 12, 8)
            
            icon = QLabel("🎧" if "Audio" in kind else ("🖱️" if "Pointer" in kind else "⌨️"))
            icon.setStyleSheet("font-size: 16px;")
            card_lay.addWidget(icon)
            
            txt_lay = QVBoxLayout()
            txt_lay.setSpacing(1)
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #2c3e50;")
            kind_lbl = QLabel(kind)
            kind_lbl.setStyleSheet("font-size: 9px; color: #7f8c8d;")
            txt_lay.addWidget(name_lbl)
            txt_lay.addWidget(kind_lbl)
            card_lay.addLayout(txt_lay)
            card_lay.addStretch()
            
            status_lbl = QLabel(status)
            status_lbl.setStyleSheet("font-size: 10px; color: #2ec27e;" if status == "Connected" else "font-size: 10px; color: #7f8c8d;")
            card_lay.addWidget(status_lbl)
            
            # Action button
            act_btn = QPushButton("Disconnect" if status == "Connected" else "Connect")
            act_btn.setFixedSize(70, 20)
            act_btn.setStyleSheet("font-size: 9px; background-color: rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.1); border-radius: 4px;")
            act_btn.clicked.connect(lambda checked, n=name: self.toggle_device_connection(n))
            card_lay.addWidget(act_btn)
            
            self.dev_list_layout.addWidget(card)
        self.dev_list_layout.addStretch()

    def toggle_device_connection(self, name):
        for i, (d_name, d_kind, d_status) in enumerate(self.bt_devices):
            if d_name == name:
                new_status = "Paired" if d_status == "Connected" else "Connected"
                self.bt_devices[i] = (d_name, d_kind, new_status)
                break
        self.refresh_bluetooth_list()

    def pair_bluetooth_action(self):
        # Pairing simulation
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Add a Device")
        dialog.setText("Searching for bluetooth devices nearby...")
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
        
        # Scan simulation
        QTimer.singleShot(2000, lambda: self.finish_bluetooth_scan(dialog))
        dialog.exec()

    def finish_bluetooth_scan(self, dialog):
        if not dialog.isVisible():
            return
        dialog.close()
        
        # Discover device
        new_dev, ok = QInputDialog.getItem(self, "Device Discovered", "Select device to pair:", ["NestSpeaker Mini", "CooController 1S"], 0, False)
        if ok and new_dev:
            # Pair
            msg = QMessageBox(self)
            msg.setWindowTitle("Pairing")
            msg.setText(f"Pairing with {new_dev}...")
            msg.show()
            
            def add_device():
                msg.close()
                self.bt_devices.append((new_dev, "Audio device" if "Speaker" in new_dev else "Gamepad", "Connected"))
                self.refresh_bluetooth_list()
                QMessageBox.information(self, "Success", f"{new_dev} successfully paired and connected!")
                
            QTimer.singleShot(1500, add_device)

    # ================= PAGE 3: Network & Internet Page =================
    def create_network_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Network & Internet", page)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26;")
        layout.addWidget(title)
        
        # Wi-Fi Enable Box
        enable_box = QFrame()
        enable_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        enable_lay = QHBoxLayout(enable_box)
        
        wifi_lbl = QLabel("Wi-Fi Interface")
        wifi_lbl.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        enable_lay.addWidget(wifi_lbl)
        enable_lay.addStretch()
        
        self.wifi_toggle = QPushButton("ON")
        self.wifi_toggle.setFixedSize(50, 24)
        self.wifi_toggle.setStyleSheet("background-color: #2ec27e; color: white; border-radius: 4px; font-weight: bold;")
        self.wifi_toggle.clicked.connect(self.toggle_wifi)
        enable_lay.addWidget(self.wifi_toggle)
        layout.addWidget(enable_box)
        
        # Networks list
        net_title = QLabel("Available Nest Networks (Wi-Fi):")
        net_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(net_title)
        
        self.net_scroll = QScrollArea()
        self.net_scroll.setWidgetResizable(True)
        self.net_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.net_widget = QWidget()
        self.net_list_layout = QVBoxLayout(self.net_widget)
        self.net_list_layout.setContentsMargins(0, 0, 10, 0)
        self.net_list_layout.setSpacing(8)
        
        self.wifi_networks = [("Loading networks...", False, "")]
        self.refresh_wifi_list()
        
        QTimer.singleShot(100, self.async_load_networks)
        
        self.net_scroll.setWidget(self.net_widget)
        layout.addWidget(self.net_scroll)
        self.stack.addWidget(page)

    def toggle_wifi(self):
        self.wifi_enabled = not self.wifi_enabled
        if self.wifi_enabled:
            self.wifi_toggle.setText("ON")
            self.wifi_toggle.setStyleSheet("background-color: #2ec27e; color: white; border-radius: 4px; font-weight: bold;")
            self.net_scroll.setEnabled(True)
        else:
            self.wifi_toggle.setText("OFF")
            self.wifi_toggle.setStyleSheet("background-color: #7f8c8d; color: white; border-radius: 4px; font-weight: bold;")
            self.net_scroll.setEnabled(False)

    def fetch_real_wifi_networks(self):
        import subprocess, sys
        networks = []
        try:
            if sys.platform.startswith("linux"):
                res = subprocess.run(["nmcli", "-t", "-f", "SSID,SECURITY,IN-USE", "dev", "wifi", "list"], capture_output=True, text=True, timeout=2)
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        parts = line.split(":")
                        if len(parts) >= 3:
                            ssid = parts[0].strip()
                            if not ssid: continue
                            sec = parts[1].strip()
                            in_use = (parts[2].strip() == "*")
                            is_secure = sec != "" and sec != "--"
                            status = "Connected, Secure" if in_use and is_secure else ("Connected" if in_use else ("Secure" if is_secure else "Open Network"))
                            if not any(n[0] == ssid for n in networks):
                                networks.append((ssid, is_secure, status))
            elif sys.platform == "win32":
                res = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True, timeout=2)
                if res.returncode == 0:
                    lines = res.stdout.splitlines()
                    for line in lines:
                        if "SSID" in line and ":" in line:
                            ssid = line.split(":", 1)[1].strip()
                            if ssid:
                                if not any(n[0] == ssid for n in networks):
                                    networks.append((ssid, True, "Secure"))
                        elif ("Auth" in line or "Autentica" in line) and ":" in line and networks:
                            auth = line.split(":", 1)[1].strip()
                            is_secure = auth != "Open" and auth != "Aperta"
                            ssid = networks[-1][0]
                            networks[-1] = (ssid, is_secure, "Secure" if is_secure else "Open Network")
        except Exception:
            pass
            
        if not networks:
            networks = [
                ("NestLink_5G", True, "Connected, Secure"),
                ("CrumbNet_Secure", True, "Secure"),
                ("PigeonCarrier_2.4G", True, "Secure"),
                ("SkyHigh_Open", False, "Open Network")
            ]
        return networks

    def async_load_networks(self):
        self.wifi_networks = self.fetch_real_wifi_networks()
        self.refresh_wifi_list()

    def refresh_wifi_list(self):
        # Clear layout
        while self.net_list_layout.count():
            item = self.net_list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
                
        for ssid, secure, status in self.wifi_networks:
            card = QFrame()
            card.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
            card_lay = QHBoxLayout(card)
            card_lay.setContentsMargins(12, 8, 12, 8)
            
            icon = QLabel("📶")
            icon.setStyleSheet("font-size: 16px;")
            card_lay.addWidget(icon)
            
            txt_lay = QVBoxLayout()
            txt_lay.setSpacing(1)
            ssid_lbl = QLabel(ssid)
            ssid_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #2c3e50;")
            status_lbl = QLabel(status)
            status_lbl.setStyleSheet("font-size: 9px; color: #7f8c8d;")
            txt_lay.addWidget(ssid_lbl)
            txt_lay.addWidget(status_lbl)
            card_lay.addLayout(txt_lay)
            card_lay.addStretch()
            
            # Action button
            if status == "Connected, Secure":
                act_btn = QPushButton("Disconnect")
                act_btn.setStyleSheet("font-size: 9px; background-color: rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.1); border-radius: 4px;")
            else:
                act_btn = QPushButton("Connect")
                act_btn.setStyleSheet("font-size: 9px; background-color: #0f82df; color: white; border: none; border-radius: 4px;")
            act_btn.setFixedSize(70, 20)
            act_btn.clicked.connect(lambda checked, s=ssid: self.connect_wifi_action(s))
            card_lay.addWidget(act_btn)
            
            self.net_list_layout.addWidget(card)
        self.net_list_layout.addStretch()

    def connect_wifi_action(self, ssid):
        # Disconnect active network if any
        current_active = None
        for i, (net_ssid, secure, status) in enumerate(self.wifi_networks):
            if status == "Connected, Secure":
                current_active = i
                break
                
        # If disconnecting the active network
        if self.wifi_networks[current_active][0] == ssid:
            self.wifi_networks[current_active] = (ssid, True, "Secure")
            self.refresh_wifi_list()
            return
            
        # Connecting to a new network
        is_secure = True
        for net_ssid, secure, status in self.wifi_networks:
            if net_ssid == ssid:
                is_secure = secure
                break
                
        if is_secure:
            password, ok = QInputDialog.getText(self, "Network Security", f"Enter password for '{ssid}':", QLineEdit.EchoMode.Password)
            if not ok or not password:
                return
                
        # Show connecting progress
        msg = QMessageBox(self)
        msg.setWindowTitle("Connecting")
        msg.setText(f"Checking credentials and connecting to {ssid}...")
        msg.show()
        
        def finish_connect():
            msg.close()
            # Disconnect the old one
            if current_active is not None:
                old_ssid, old_secure, _ = self.wifi_networks[current_active]
                self.wifi_networks[current_active] = (old_ssid, old_secure, "Secure" if old_secure else "Open Network")
                
            # Connect the new one
            for i, (net_ssid, secure, status) in enumerate(self.wifi_networks):
                if net_ssid == ssid:
                    self.wifi_networks[i] = (ssid, secure, "Connected, Secure")
                    break
                    
            self.refresh_wifi_list()
            QMessageBox.information(self, "Connected", f"Successfully connected to {ssid}!")
            
        QTimer.singleShot(1500, finish_connect)

    # ================= PAGE 4: Personalization Page =================
    def create_personalization_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Personalization", page)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26;")
        layout.addWidget(title)

        desc = QLabel("Customize your desktop background colors and wallpapers.", page)
        desc.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(desc)

        # Add Dark Mode Toggle
        dark_lay = QHBoxLayout()
        dark_lbl = QLabel("Dark Mode")
        dark_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        self.dark_chk = QCheckBox()
        self.dark_chk.setChecked(theme.is_dark_mode)
        self.dark_chk.stateChanged.connect(self.toggle_dark_mode)
        dark_lay.addWidget(dark_lbl)
        dark_lay.addWidget(self.dark_chk)
        dark_lay.addStretch()
        layout.addLayout(dark_lay)

        # Add Liquid Glass Toggle
        glass_lay = QHBoxLayout()
        glass_lbl = QLabel("Enable Dynamic Liquid Glass Overlay (iOS 26 Style)")
        glass_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        self.glass_chk = QCheckBox()
        self.glass_chk.setChecked(self.desktop.liquid_glass_enabled if self.desktop else True)
        self.glass_chk.stateChanged.connect(self.toggle_liquid_glass)
        
        glass_lay.addWidget(glass_lbl)
        glass_lay.addWidget(self.glass_chk)
        glass_lay.addStretch()
        layout.addLayout(glass_lay)

        themes_title = QLabel("Choose desktop background:", page)
        themes_title.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 10px; color: #2c3e50;")
        layout.addWidget(themes_title)

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "wallpapers")
        wallpapers = []
        if os.path.exists(assets_dir):
            for file in sorted(os.listdir(assets_dir)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    name = os.path.splitext(file)[0]
                    wallpapers.append((name, file))
                    
        wallpapers.append(("Default", "wallpaper.png"))
        wallpapers.append(("Black", "black"))

        scroll = QScrollArea(page)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 16, 0)
        grid.setSpacing(12)

        for idx, (name, filename) in enumerate(wallpapers):
            row = idx // 3
            col = idx % 3

            vbox = QVBoxLayout()
            vbox.setSpacing(4)

            btn = QPushButton(grid_widget)
            btn.setFixedSize(160, 90)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if filename == "black":
                btn.setStyleSheet(
                    "QPushButton { border: 2px solid #ccc; border-radius: 8px; background-color: #050505; }"
                    "QPushButton:hover { border-color: #0f82df; }"
                )
            elif filename == "wallpaper.png":
                # Fallback path logic
                img_path = os.path.join(os.path.dirname(assets_dir), "wallpaper.png").replace("\\", "/")
                btn.setStyleSheet(
                    f"QPushButton {{ border: 2px solid #ccc; border-radius: 8px; "
                    f"background-image: url('{img_path}'); background-position: center; "
                    f"background-repeat: no-repeat; background-size: cover; }}"
                    f"QPushButton:hover {{ border-color: #0f82df; }}"
                )
            else:
                img_path = os.path.join(assets_dir, filename).replace("\\", "/")
                btn.setStyleSheet(
                    f"QPushButton {{ border: 2px solid #ccc; border-radius: 8px; "
                    f"background-image: url('{img_path}'); background-position: center; "
                    f"background-repeat: no-repeat; background-size: cover; }}"
                    f"QPushButton:hover {{ border-color: #0f82df; }}"
                )
            btn.clicked.connect(lambda checked, t=filename: self.change_wallpaper(t))

            lbl = QLabel(name, grid_widget)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-size: 10px; color: #1a1f26;")

            vbox.addWidget(btn)
            vbox.addWidget(lbl)
            grid.addLayout(vbox, row, col)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
        self.stack.addWidget(page)

    def change_wallpaper(self, wp_type):
        if self.desktop:
            self.desktop.set_wallpaper_type(wp_type)

    def toggle_dark_mode(self, state):
        from PyQt6.QtWidgets import QApplication
        enabled = (state == 2)
        theme.set_dark_mode(enabled)
        # Apply stylesheet globally
        QApplication.instance().setStyleSheet(theme.get_stylesheet())
        # Invalidate desktop caches so background is redrawn
        if self.desktop:
            self.desktop._caches_dirty = True
            self.desktop.update()
        # Save preference to disk
        try:
            import json, os
            user_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users")
            if self.desktop and self.desktop.main_window and self.desktop.main_window.fs:
                current_user = self.desktop.main_window.fs.current_user
                if current_user:
                    prefs_path = os.path.join(user_data_dir, current_user, "theme.json")
                    os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
                    with open(prefs_path, 'w') as tf:
                        json.dump({"dark_mode": enabled}, tf)
        except Exception:
            pass

    def toggle_liquid_glass(self, state):
        if self.desktop:
            self.desktop.set_liquid_glass_enabled(state == 2)

    # ================= PAGE 5: Accounts Page =================
    def create_accounts_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Accounts Manager", page)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26;")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        self.accounts_layout = QVBoxLayout(scroll_widget)
        self.accounts_layout.setContentsMargins(0, 0, 10, 0)
        self.accounts_layout.setSpacing(12)
        
        # 1. Accounts list section
        acc_list_box = QFrame()
        acc_list_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        self.acc_list_lay = QVBoxLayout(acc_list_box)
        self.acc_list_lay.setContentsMargins(15, 12, 15, 12)
        
        acc_hdr = QLabel("Registered Users")
        acc_hdr.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        self.acc_list_lay.addWidget(acc_hdr)
        
        self.users_container_widget = QWidget()
        self.users_list_layout = QVBoxLayout(self.users_container_widget)
        self.users_list_layout.setContentsMargins(0, 0, 0, 0)
        self.users_list_layout.setSpacing(6)
        
        self.refresh_accounts_list()
        
        self.acc_list_lay.addWidget(self.users_container_widget)
        self.accounts_layout.addWidget(acc_list_box)
        
        # 2. Add New User Section
        add_box = QFrame()
        add_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        add_lay = QVBoxLayout(add_box)
        add_lay.setContentsMargins(15, 12, 15, 12)
        add_lay.setSpacing(8)
        
        add_hdr = QLabel("Add New User Account")
        add_hdr.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        add_lay.addWidget(add_hdr)
        
        self.new_user_input = QLineEdit()
        self.new_user_input.setPlaceholderText("New username")
        self.new_user_input.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 6px; font-size: 11px;")
        add_lay.addWidget(self.new_user_input)
        
        self.new_pass_input = QLineEdit()
        self.new_pass_input.setPlaceholderText("New password")
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 6px; font-size: 11px;")
        add_lay.addWidget(self.new_pass_input)
        
        btn_add = QPushButton("Add User")
        btn_add.setStyleSheet("background-color: #0f82df; color: white; padding: 6px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        btn_add.clicked.connect(self.add_user_action)
        add_lay.addWidget(btn_add)
        self.accounts_layout.addWidget(add_box)
        
        # 3. Change Current Password Section
        change_box = QFrame()
        change_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        change_lay = QVBoxLayout(change_box)
        change_lay.setContentsMargins(15, 12, 15, 12)
        change_lay.setSpacing(8)
        
        change_hdr = QLabel("Change Your Password")
        change_hdr.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        change_lay.addWidget(change_hdr)
        
        self.curr_pass_input = QLineEdit()
        self.curr_pass_input.setPlaceholderText("New password")
        self.curr_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.curr_pass_input.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 6px; font-size: 11px;")
        change_lay.addWidget(self.curr_pass_input)
        
        btn_change = QPushButton("Update Password")
        btn_change.setStyleSheet("background-color: #2ec27e; color: white; padding: 6px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        btn_change.clicked.connect(self.change_password_action)
        change_lay.addWidget(btn_change)
        self.accounts_layout.addWidget(change_box)
        
        self.accounts_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        self.stack.addWidget(page)

    def refresh_accounts_list(self):
        # Clear layout
        while self.users_list_layout.count():
            item = self.users_list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
                
        users = users_helper.load_users()
        current_username = "Sky Pigeon"
        if self.desktop and self.desktop.main_window and self.desktop.main_window.fs:
            current_username = self.desktop.main_window.fs.current_user or "Sky Pigeon"
            
        for username in users:
            row = QFrame()
            row.setStyleSheet("background-color: rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.04); border-radius: 4px;")
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(10, 6, 10, 6)
            
            lbl = QLabel(username)
            lbl.setStyleSheet("font-size: 11px; color: #2c3e50; font-weight: bold;")
            row_lay.addWidget(lbl)
            
            if username == current_username:
                badge = QLabel("(Current User)")
                badge.setStyleSheet("font-size: 9px; color: #0f82df; font-style: italic;")
                row_lay.addWidget(badge)
                row_lay.addStretch()
            else:
                row_lay.addStretch()
                del_btn = QPushButton("Delete")
                del_btn.setFixedSize(50, 18)
                del_btn.setStyleSheet("font-size: 9px; background-color: #ff4a4a; color: white; border: none; border-radius: 3px;")
                del_btn.clicked.connect(lambda checked, u=username: self.delete_user_action(u))
                row_lay.addWidget(del_btn)
                
            self.users_list_layout.addWidget(row)

    def add_user_action(self):
        uname = self.new_user_input.text().strip()
        upass = self.new_pass_input.text().strip()
        if uname and upass:
            users = users_helper.load_users()
            if uname in users:
                QMessageBox.warning(self, "Warning", f"Username '{uname}' already exists.")
                return
            users[uname] = upass
            users_helper.save_users(users)
            self.new_user_input.clear()
            self.new_pass_input.clear()
            self.refresh_accounts_list()
            QMessageBox.information(self, "Success", f"User '{uname}' added successfully!")
            
            # Refresh login screen if visible
            main_win = self.desktop.main_window if self.desktop else None
            if main_win and hasattr(main_win, 'login_screen'):
                main_win.login_screen.reload_users()
        else:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")

    def delete_user_action(self, username):
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete user '{username}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            users = users_helper.load_users()
            if username in users:
                del users[username]
                users_helper.save_users(users)
                self.refresh_accounts_list()
                
                # Refresh login screen
                main_win = self.desktop.main_window if self.desktop else None
                if main_win and hasattr(main_win, 'login_screen'):
                    main_win.login_screen.reload_users()

    def change_password_action(self):
        new_pass = self.curr_pass_input.text().strip()
        current_username = "Sky Pigeon"
        if self.desktop and self.desktop.main_window and self.desktop.main_window.fs:
            current_username = self.desktop.main_window.fs.current_user or "Sky Pigeon"
            
        if new_pass:
            users = users_helper.load_users()
            if current_username in users:
                users[current_username] = new_pass
                users_helper.save_users(users)
                self.curr_pass_input.clear()
                QMessageBox.information(self, "Success", "Password updated successfully!")
        else:
            QMessageBox.warning(self, "Error", "Please enter a password.")

    # ================= PAGE 6: Power & Battery Page =================
    def create_power_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("Power & Battery Settings", page)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26;")
        layout.addWidget(title)
        
        # Battery Health block
        bat_box = QFrame()
        bat_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        bat_lay = QVBoxLayout(bat_box)
        bat_lay.setContentsMargins(15, 12, 15, 12)
        
        # Read real host battery using psutil (if installed)
        percent = 84
        charging = True
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                charging = battery.power_plugged
        except:
            pass
            
        bat_hdr = QHBoxLayout()
        bat_icon = QLabel("🔌" if charging else "🔋")
        bat_icon.setStyleSheet("font-size: 18px;")
        bat_hdr.addWidget(bat_icon)
        
        self.bat_lbl = QLabel(f"Battery Percentage: {percent}% ({'Charging' if charging else 'On Battery'})")
        self.bat_lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        bat_hdr.addWidget(self.bat_lbl)
        bat_hdr.addStretch()
        bat_lay.addLayout(bat_hdr)
        
        self.bat_progress = QProgressBar()
        self.bat_progress.setValue(percent)
        self.bat_progress.setFixedHeight(12)
        self.bat_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 4px;
                background-color: #f1f2f6;
                text-align: center;
                font-size: 8px;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #2ec27e;
                border-radius: 3px;
            }
        """)
        bat_lay.addWidget(self.bat_progress)
        layout.addWidget(bat_box)
        
        # Plan selection
        plan_box = QFrame()
        plan_box.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.06); border-radius: 8px;")
        plan_lay = QVBoxLayout(plan_box)
        plan_lay.setContentsMargins(15, 12, 15, 12)
        plan_lay.setSpacing(10)
        
        plan_hdr = QLabel("Power Configuration Profile:")
        plan_hdr.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        plan_lay.addWidget(plan_hdr)
        
        row1 = QHBoxLayout()
        lbl1 = QLabel("Power Plan Profile:")
        lbl1.setStyleSheet("font-size: 11px; color: #2c3e50;")
        combo1 = QComboBox()
        combo1.addItems(["Eco Nesting Mode", "Balanced Flight Plan", "High Frequency Performance"])
        combo1.setCurrentIndex(1)
        combo1.setStyleSheet("background-color: white; border: 1px solid #ccc; padding: 4px; font-size: 11px;")
        row1.addWidget(lbl1)
        row1.addWidget(combo1)
        row1.addStretch()
        plan_lay.addLayout(row1)
        
        row2 = QHBoxLayout()
        lbl2 = QLabel("Sleep Timeout Profile:")
        lbl2.setStyleSheet("font-size: 11px; color: #2c3e50;")
        combo2 = QComboBox()
        combo2.addItems(["Never", "1 Minute", "5 Minutes", "10 Minutes", "30 Minutes"])
        combo2.setCurrentIndex(2)
        combo2.setStyleSheet("background-color: white; border: 1px solid #ccc; padding: 4px; font-size: 11px;")
        row2.addWidget(lbl2)
        row2.addWidget(combo2)
        row2.addStretch()
        plan_lay.addLayout(row2)
        
        layout.addWidget(plan_box)
        layout.addStretch()
        self.stack.addWidget(page)

    # ================= PAGE 7: About Page (About Sigeon OS) =================
    def create_about_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Left Side (Logo + Info)
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo = QLabel(left)
        logo.setPixmap(theme.IconFactory.get_icon("logo", 96).pixmap(96, 96))
        left_lay.addWidget(logo)
        
        title = QLabel("Sigeon OS", left)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        left_lay.addWidget(title)
        
        ver = QLabel("10.0.0 (Blue Feather Update)", left)
        ver.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        left_lay.addWidget(ver)
        
        desc = QLabel("Keeping the sky smooth\nand the cooing strong. 🕊️", left)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 10px; color: #95a5a6; margin-top: 8px; font-style: italic;")
        left_lay.addWidget(desc)
        
        layout.addWidget(left, stretch=1)
        
        # Right Side (System Specs)
        right = QFrame()
        right.setStyleSheet("background-color: #f7fafc; border: 1px solid rgba(0,0,0,0.05); border-radius: 8px; padding: 12px;")
        right_lay = QVBoxLayout(right)
        
        # Generate real specs dynamically
        device_name = platform.node()
        processor = platform.processor() or "Unknown Processor"
        ram = "8.0 GB"
        try:
            import psutil
            total_bytes = psutil.virtual_memory().total
            ram_gb = total_bytes / (1024 ** 3)
            ram = f"{ram_gb:.1f} GB"
        except:
            pass
            
        system_type = f"{platform.system()} {platform.release()}"
        pigeon_id = "SP-2026-BLUE-0626"
        os_version = "10.0.0 (Blue Feather Update)\nBuild 2026.06.26"

        specs = [
            ("Device name", device_name),
            ("Processor", processor),
            ("Installed RAM", ram),
            ("System type", system_type),
            ("Pigeon ID", pigeon_id),
            ("Sigeon OS", os_version)
        ]
        
        for name, value in specs:
            row = QWidget()
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(0, 4, 0, 4)
            
            lbl_name = QLabel(name, row)
            lbl_name.setFixedWidth(100)
            lbl_name.setStyleSheet("font-weight: bold; font-size: 11px; color: #2c3e50;")
            
            lbl_val = QLabel(value, row)
            lbl_val.setStyleSheet("font-size: 11px; color: #1a1f26;")
            lbl_val.setWordWrap(True)
            
            row_lay.addWidget(lbl_name)
            row_lay.addWidget(lbl_val)
            right_lay.addWidget(row)
            
        right_lay.addStretch()
        
        # Copy Specs Button
        btn_copy = QPushButton("Copy specs", right)
        btn_copy.setObjectName("settings_primary_btn")
        btn_copy.setStyleSheet(theme.get_stylesheet())
        btn_copy.clicked.connect(self.copy_specs_action)
        right_lay.addWidget(btn_copy, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(right, stretch=2)
        self.stack.addWidget(page)

    def copy_specs_action(self):
        # Action feedback
        btn = self.sender()
        if btn:
            btn.setText("Copied!")
            QTimer.singleShot(1500, lambda: btn.setText("Copy specs"))
