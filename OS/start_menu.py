import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QGridLayout, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import theme
import animations

class SigeonStartMenu(QWidget):
    app_launch_requested = pyqtSignal(str)
    file_open_requested = pyqtSignal(str)
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.init_ui()

    def init_ui(self):
        self.setObjectName("start_menu_frame")
        self.setFixedSize(340, 480)
        self.setStyleSheet("""
            QWidget#start_menu_frame {
                background-color: rgba(26, 30, 41, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }
        """)

        # Add drop shadow
        animations.add_drop_shadow(self, blur=20, offset_x=0, offset_y=4)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 12)
        self.layout.setSpacing(14)

        # 1. Search Bar
        self.search_container = QFrame(self)
        self.search_container.setFixedHeight(36)
        self.search_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 18px;
            }
        """)
        self.search_lay = QHBoxLayout(self.search_container)
        self.search_lay.setContentsMargins(12, 0, 12, 0)
        
        self.search_icon = QLabel("🔍", self.search_container)
        self.search_icon.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 14px;")
        self.search_lay.addWidget(self.search_icon)

        self.search_input = QLineEdit(self.search_container)
        self.search_input.setPlaceholderText("Search apps, files, or web...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 13px;
            }
        """)
        self.search_lay.addWidget(self.search_input, stretch=1)
        self.layout.addWidget(self.search_container)

        # 2. Pinned Apps Section
        self.pinned_lbl = QLabel("Pinned", self)
        self.pinned_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        self.layout.addWidget(self.pinned_lbl)

        self.apps_grid = QWidget(self)
        self.grid_lay = QGridLayout(self.apps_grid)
        self.grid_lay.setContentsMargins(0, 0, 0, 0)
        self.grid_lay.setHorizontalSpacing(10)
        self.grid_lay.setVerticalSpacing(16)

        pinned_apps = [
            ("Files", "folder", "explorer"),
            ("Paint", "photos", "paint"),
            ("Notes", "notepad", "notepad"),
            ("Settings", "settings", "settings"),
            ("Terminal", "terminal", "terminal"),
            ("Calendar", "settings", "calendar"),
            ("Flappy Bird", "logo", "flappy_game")
        ]

        for i, (name, icon_name, app_id) in enumerate(pinned_apps):
            row = i // 3
            col = i % 3
            btn = self.create_app_btn(name, icon_name, app_id)
            self.grid_lay.addWidget(btn, row, col)

        self.layout.addWidget(self.apps_grid)
        self.layout.addStretch()

        # 3. Recommended / Recent Section (Removed)
        self.layout.addStretch()

        # 4. Bottom Profile Section
        self.bottom_bar = QWidget(self)
        self.bottom_bar.setFixedHeight(48)
        self.bottom_bar.setStyleSheet("border-top: 1px solid rgba(255, 255, 255, 0.1);")
        
        self.bottom_lay = QHBoxLayout(self.bottom_bar)
        self.bottom_lay.setContentsMargins(0, 10, 0, 0)
        
        self.prof_icon = QLabel(self.bottom_bar)
        self.prof_icon.setPixmap(theme.IconFactory.get_icon("logo", 24).pixmap(24, 24))
        self.bottom_lay.addWidget(self.prof_icon)

        # IMPORTANT: main.py accesses self.menu.prof_name.setText()
        self.prof_name = QLabel("User", self.bottom_bar)
        self.prof_name.setStyleSheet("color: white; font-size: 13px; font-weight: 500;")
        self.bottom_lay.addWidget(self.prof_name)

        self.bottom_lay.addStretch()

        self.btn_logout = QPushButton("🚪", self.bottom_bar)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #ff9f43;
            }
        """)
        self.btn_logout.clicked.connect(self.logout_requested.emit)
        self.bottom_lay.addWidget(self.btn_logout)

        self.btn_power = QPushButton("⏻", self.bottom_bar)
        self.btn_power.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #ff4a4a;
            }
        """)
        self.btn_power.clicked.connect(self.shutdown)
        self.bottom_lay.addWidget(self.btn_power)

        self.layout.addWidget(self.bottom_bar)

    def create_app_btn(self, name, icon_name, app_id):
        btn = QPushButton(self)
        btn.setFixedSize(86, 76)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        lay = QVBoxLayout(btn)
        lay.setContentsMargins(4, 8, 4, 8)
        lay.setSpacing(6)
        
        ico_lbl = QLabel(btn)
        ico_lbl.setPixmap(theme.IconFactory.get_icon(icon_name, 32).pixmap(32, 32))
        ico_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        txt_lbl = QLabel(name, btn)
        txt_lbl.setStyleSheet("color: white; font-size: 11px;")
        txt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lay.addWidget(ico_lbl)
        lay.addWidget(txt_lbl)
        
        btn.clicked.connect(lambda checked, a=app_id, b=btn: self.on_app_clicked(a, b))
        return btn

    def create_rec_btn(self, name, icon_name, action_id):
        btn = QPushButton(self)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border-radius: 6px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        lay = QHBoxLayout(btn)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(12)
        
        ico_lbl = QLabel(btn)
        ico_lbl.setPixmap(theme.IconFactory.get_icon(icon_name, 20).pixmap(20, 20))
        
        txt_lbl = QLabel(name, btn)
        txt_lbl.setStyleSheet("color: white; font-size: 12px;")
        
        lay.addWidget(ico_lbl)
        lay.addWidget(txt_lbl)
        lay.addStretch()
        
        btn.clicked.connect(lambda checked, a=action_id: self.file_open_requested.emit(a))
        return btn

    def on_app_clicked(self, app_id, btn):
        animations.bounce(btn, duration=300)
        self.app_launch_requested.emit(app_id)

    def shutdown(self):
        import sys
        sys.exit(0)