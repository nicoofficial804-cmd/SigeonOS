import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QListWidget, QListWidgetItem, QStackedWidget,
                             QFrame, QProgressBar, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QColor
import theme

class SigeonSettings(QWidget):
    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.init_ui()

    def init_ui(self):
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 1. Left Sidebar
        self.sidebar = QWidget(self)
        self.sidebar.setObjectName("settings_sidebar")
        self.sidebar.setFixedWidth(180)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 12, 0, 12)
        
        # Header profile
        self.profile_widget = QWidget(self.sidebar)
        self.profile_layout = QHBoxLayout(self.profile_widget)
        self.profile_layout.setContentsMargins(12, 0, 12, 12)
        
        self.profile_pic = QLabel(self.profile_widget)
        self.profile_pic.setPixmap(theme.IconFactory.get_icon("logo_white", 28).pixmap(28, 28))
        self.profile_layout.addWidget(self.profile_pic)
        
        self.profile_text = QWidget(self.profile_widget)
        self.pt_layout = QVBoxLayout(self.profile_text)
        self.pt_layout.setContentsMargins(0, 0, 0, 0)
        self.pt_layout.setSpacing(0)
        self.profile_name = QLabel("Sky Pigeon", self.profile_text)
        self.profile_name.setStyleSheet("font-weight: bold; font-size: 11px; color: #1a1f26;")
        self.profile_email = QLabel("sky@pigeon.os", self.profile_text)
        self.profile_email.setStyleSheet("font-size: 9px; color: #7f8c8d;")
        self.pt_layout.addWidget(self.profile_name)
        self.pt_layout.addWidget(self.profile_email)
        self.profile_layout.addWidget(self.profile_text)
        
        self.sidebar_layout.addWidget(self.profile_widget)
        
        # Search Box
        self.search_box = QLineEdit(self.sidebar)
        self.search_box.setPlaceholderText("Search settings")
        self.search_box.setStyleSheet("background-color: rgba(255,255,255,0.8); border: 1px solid #dcdde1; border-radius: 4px; padding: 4px 8px; margin: 0px 10px 10px 10px; font-size: 11px;")
        self.sidebar_layout.addWidget(self.search_box)
        
        # Sidebar Menu
        self.menu_list = QListWidget(self.sidebar)
        self.menu_list.setObjectName("settings_sidebar_list")
        self.menu_list.currentRowChanged.connect(self.menu_changed)
        
        self.add_menu_item("System", "settings")
        self.add_menu_item("Bluetooth & Devices", "wing_drive")
        self.add_menu_item("Network & Internet", "cloud_nest")
        self.add_menu_item("Personalization", "photos")
        self.add_menu_item("Accounts", "logo")
        self.add_menu_item("Sound", "folder_music")
        self.add_menu_item("Power & Battery", "recycle_empty")
        self.add_menu_item("About Sigeon OS", "logo_white")
        
        self.sidebar_layout.addWidget(self.menu_list)
        self.layout.addWidget(self.sidebar)
        
        # 2. Right Stacked Widget
        self.stack = QStackedWidget(self)
        self.layout.addWidget(self.stack, stretch=1)
        
        # Initialize pages
        self.create_system_page()
        self.create_generic_page("Bluetooth & Devices", "Pair and manage your coop-tooth controllers and feathers.")
        self.create_generic_page("Network & Internet", "Configure Wi-Fi nests and data migration patterns.")
        self.create_personalization_page()
        self.create_accounts_page()
        self.create_generic_page("Sound", "Volume mixer, audio nests, and vocal frequency tuning.")
        self.create_generic_page("Power & Battery", "Adjust energy hibernation states for battery nesting.")
        self.create_about_page()
        
        self.menu_list.setCurrentRow(0)

    def add_menu_item(self, name, icon_name):
        item = QListWidgetItem(name)
        item.setIcon(theme.IconFactory.get_icon(icon_name, 16))
        self.menu_list.addItem(item)

    def menu_changed(self, index):
        self.stack.setCurrentIndex(index)

    # PAGE 1: System Page
    def create_system_page(self):
        page = QWidget()
        page_layout = QHBoxLayout(page)
        page_layout.setContentsMargins(16, 16, 16, 16)
        page_layout.setSpacing(12)
        
        # Left main list of settings
        left_area = QScrollArea()
        left_area.setWidgetResizable(True)
        left_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        title = QLabel("System", left_widget)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26; margin-bottom: 8px;")
        left_layout.addWidget(title)
        
        # Grid/list of items
        items = [
            ("Display", "Brightness, night light, display profile", "photos"),
            ("Sound", "Volume levels, output, input", "folder_music"),
            ("Power & Battery", "Battery usage, battery saver", "recycle_empty"),
            ("Storage", "Storage usage, cleanup recommendations", "pigeon_drive")
        ]
        
        for name, sub, icon in items:
            card = QFrame(left_widget)
            card.setObjectName("settings_item_card")
            card.setStyleSheet(theme.get_stylesheet())
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            
            icon_lbl = QLabel(card)
            icon_lbl.setPixmap(theme.IconFactory.get_icon(icon, 24).pixmap(24, 24))
            card_layout.addWidget(icon_lbl)
            
            text_layout = QVBoxLayout()
            text_layout.setSpacing(1)
            name_lbl = QLabel(name, card)
            name_lbl.setStyleSheet("font-weight: 600; font-size: 12px; color: #2c3e50;")
            sub_lbl = QLabel(sub, card)
            sub_lbl.setStyleSheet("font-size: 10px; color: #7f8c8d;")
            text_layout.addWidget(name_lbl)
            text_layout.addWidget(sub_lbl)
            card_layout.addLayout(text_layout)
            card_layout.addStretch()
            
            arrow_lbl = QLabel("›", card)
            arrow_lbl.setStyleSheet("font-size: 16px; color: #bdc3c7;")
            card_layout.addWidget(arrow_lbl)
            
            left_layout.addWidget(card)
            
        left_area.setWidget(left_widget)
        page_layout.addWidget(left_area, stretch=3)
        
        # Right info card (Sigeon OS version specs)
        right_card = QFrame(page)
        right_card.setStyleSheet("background-color: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.06); border-radius: 10px;")
        right_card.setFixedWidth(180)
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(12, 16, 12, 16)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        logo = QLabel(right_card)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setPixmap(theme.IconFactory.get_icon("logo", 72).pixmap(72, 72))
        right_layout.addWidget(logo)
        
        os_title = QLabel("Sigeon OS", right_card)
        os_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        os_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #2c3e50; margin-top: 8px;")
        right_layout.addWidget(os_title)
        
        version_lbl = QLabel("10.0.0 (Blue Feather Update)", right_card)
        version_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_lbl.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        right_layout.addWidget(version_lbl)
        
        build_lbl = QLabel("Build 2024.5.20", right_card)
        build_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        build_lbl.setStyleSheet("font-size: 9px; color: #95a5a6; margin-bottom: 12px;")
        right_layout.addWidget(build_lbl)
        
        sep = QFrame(right_card)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(0,0,0,0.06); border: none; height: 1px; margin: 4px 0px;")
        right_layout.addWidget(sep)
        
        status_lbl = QLabel("Your system is up to date.\nLast checked: Today, 9:33 AM", right_card)
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_lbl.setStyleSheet("font-size: 10px; color: #2c3e50; margin: 8px 0px;")
        right_layout.addWidget(status_lbl)
        
        self.btn_check_update = QPushButton("Check for updates", right_card)
        self.btn_check_update.setObjectName("settings_primary_btn")
        self.btn_check_update.setStyleSheet(theme.get_stylesheet())
        self.btn_check_update.clicked.connect(lambda: self.menu_list.setCurrentRow(9)) # Go to updates tab
        right_layout.addWidget(self.btn_check_update)
        
        page_layout.addWidget(right_card, stretch=1)
        self.stack.addWidget(page)

    # PAGE 2: Generic Placeholder Page
    def create_generic_page(self, title, desc):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title, page)
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26;")
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel(desc, page)
        lbl_desc.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-top: 10px;")
        layout.addWidget(lbl_desc)
        layout.addStretch()
        
        self.stack.addWidget(page)

    # PAGE 3: Personalization Page
    def create_personalization_page(self):
        import os
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

        themes_title = QLabel("Choose desktop background:", page)
        themes_title.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 10px; color: #2c3e50;")
        layout.addWidget(themes_title)

        # Build list of wallpapers from assets/wallpapers directory
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "wallpapers")
        wallpapers = []
        if os.path.exists(assets_dir):
            for file in sorted(os.listdir(assets_dir)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    name = os.path.splitext(file)[0]  # filename without extension
                    wallpapers.append((name, file))

        if not wallpapers:
            no_wp = QLabel("No wallpapers found in assets/wallpapers.", page)
            no_wp.setStyleSheet("font-size: 11px; color: #95a5a6;")
            layout.addWidget(no_wp)
            layout.addStretch()
            self.stack.addWidget(page)
            return

        # Scrollable area for the grid
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

    def create_accounts_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Accounts", page)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1f26;")
        layout.addWidget(title)
        
        desc = QLabel("Manage users on this PC.", page)
        desc.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(desc)
        
        self.new_user_input = QLineEdit(page)
        self.new_user_input.setPlaceholderText("New username")
        self.new_user_input.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 6px;")
        layout.addWidget(self.new_user_input)
        
        self.new_pass_input = QLineEdit(page)
        self.new_pass_input.setPlaceholderText("New password")
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px; padding: 6px;")
        layout.addWidget(self.new_pass_input)
        
        btn_add = QPushButton("Add User", page)
        btn_add.setStyleSheet("background-color: #0f82df; color: white; padding: 6px; border-radius: 4px;")
        btn_add.clicked.connect(self.add_user_action)
        layout.addWidget(btn_add)
        
        self.user_msg = QLabel("", page)
        self.user_msg.setStyleSheet("color: green;")
        layout.addWidget(self.user_msg)
        
        layout.addStretch()
        self.stack.addWidget(page)

    def add_user_action(self):
        import users
        uname = self.new_user_input.text().strip()
        upass = self.new_pass_input.text().strip()
        if uname and upass:
            users.add_user(uname, upass)
            self.user_msg.setText("User added successfully!")
            self.new_user_input.clear()
            self.new_pass_input.clear()
        else:
            self.user_msg.setStyleSheet("color: red;")
            self.user_msg.setText("Please enter username and password.")

    def change_wallpaper(self, wp_type):
        if self.desktop:
            self.desktop.set_wallpaper_type(wp_type)

    # PAGE 4: Updates Page (Update Center)
    def create_updates_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Left small menu
        side_menu = QWidget()
        side_menu.setObjectName("explorer_sidebar") # share theme color
        side_menu.setFixedWidth(140)
        side_layout = QVBoxLayout(side_menu)
        side_layout.setContentsMargins(0, 10, 0, 10)
        
        side_list = QListWidget(side_menu)
        side_list.setObjectName("explorer_sidebar_list")
        side_list.addItem("Overview")
        side_list.addItem("Update history")
        side_list.addItem("Advanced options")
        side_list.addItem("Change settings")
        side_list.setCurrentRow(0)
        side_layout.addWidget(side_list)
        layout.addWidget(side_menu)
        
        # Right Main Panel
        self.update_main = QWidget()
        self.update_main.setStyleSheet("background-color: #ffffff;")
        self.up_layout = QVBoxLayout(self.update_main)
        self.up_layout.setContentsMargins(20, 20, 20, 20)
        self.up_layout.setSpacing(12)
        
        self.update_title = QLabel("Update Center", self.update_main)
        self.update_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1f26;")
        self.up_layout.addWidget(self.update_title)
        
        # Status Card
        self.status_card = QFrame(self.update_main)
        self.status_card.setStyleSheet("background-color: #f7fafc; border: 1px solid rgba(0,0,0,0.05); border-radius: 8px; padding: 12px;")
        self.card_lay = QHBoxLayout(self.status_card)
        
        self.status_icon = QLabel(self.status_card)
        self.status_icon.setPixmap(theme.IconFactory.get_icon("logo", 40).pixmap(40, 40)) # Green dot check
        self.card_lay.addWidget(self.status_icon)
        
        self.status_text_lay = QVBoxLayout()
        self.status_text_lay.setSpacing(2)
        self.status_title = QLabel("You're up to date!", self.status_card)
        self.status_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        self.status_time = QLabel("Last checked: Today, 9:33 AM", self.status_card)
        self.status_time.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        self.status_text_lay.addWidget(self.status_title)
        self.status_text_lay.addWidget(self.status_time)
        self.card_lay.addLayout(self.status_text_lay)
        self.card_lay.addStretch()
        
        self.btn_action = QPushButton("Check for updates", self.status_card)
        self.btn_action.setObjectName("settings_primary_btn")
        self.btn_action.setStyleSheet(theme.get_stylesheet())
        self.btn_action.clicked.connect(self.start_checking_updates)
        self.card_lay.addWidget(self.btn_action)
        
        self.up_layout.addWidget(self.status_card)
        
        # Progress Bar for checking updates (hidden initially)
        self.progress = QProgressBar(self.update_main)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar { border: 1px solid #dcdde1; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #0f82df; }")
        self.up_layout.addWidget(self.progress)
        
        # Details Card
        det_card = QFrame(self.update_main)
        det_card.setStyleSheet("background-color: #ffffff; border: 1px solid rgba(0,0,0,0.05); border-radius: 8px; padding: 10px;")
        det_lay = QVBoxLayout(det_card)
        det_lay.setSpacing(4)
        
        ver_lbl = QLabel("10.0.0 (Blue Feather Update)", det_card)
        ver_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #2c3e50;")
        inst_lbl = QLabel("Installed on May 20, 2024", det_card)
        inst_lbl.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        link_lbl = QLabel("See what's new", det_card)
        link_lbl.setStyleSheet("font-size: 10px; color: #0f82df; text-decoration: underline;")
        
        det_lay.addWidget(ver_lbl)
        det_lay.addWidget(inst_lbl)
        det_lay.addWidget(link_lbl)
        self.up_layout.addWidget(det_card)
        
        self.up_layout.addStretch()
        
        footer_link = QLabel("Looking for earlier updates? Visit the Sigeon OS archive", self.update_main)
        footer_link.setStyleSheet("font-size: 9px; color: #7f8c8d; text-decoration: underline;")
        self.up_layout.addWidget(footer_link)
        
        layout.addWidget(self.update_main)
        self.stack.addWidget(page)

    def start_checking_updates(self):
        self.btn_action.setEnabled(False)
        self.progress.setValue(0)
        self.progress.setVisible(True)
        self.status_title.setText("Checking for updates...")
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.tick_update_check)
        self.update_timer.start(100)

    def tick_update_check(self):
        val = self.progress.value() + 5
        self.progress.setValue(val)
        if val >= 100:
            self.update_timer.stop()
            self.progress.setVisible(False)
            self.btn_action.setEnabled(True)
            self.status_title.setText("You're up to date!")
            self.status_time.setText("Last checked: Just now")

    # PAGE 5: About Page (About Sigeon OS)
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
        
        import platform
        # Generate real specs dynamically
        try:
            import psutil
            has_psutil = True
        except ImportError:
            has_psutil = False

        device_name = platform.node()
        processor = platform.processor() or "Unknown"
        ram = "Unknown"
        if has_psutil:
            total_bytes = psutil.virtual_memory().total
            ram_gb = total_bytes / (1024 ** 3)
            ram = f"{ram_gb:.1f} GB"
        else:
            try:
                import os
                if hasattr(os, 'sysconf'):
                    total_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
                    ram_gb = total_bytes / (1024 ** 3)
                    ram = f"{ram_gb:.1f} GB"
            except Exception:
                pass
        system_type = f"{platform.system()} {platform.release()}"
        pigeon_id = "SP-2024-BLUE-0920"
        os_version = "10.0.0 (Blue Feather Update)\nBuild 2024.5.20"

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
