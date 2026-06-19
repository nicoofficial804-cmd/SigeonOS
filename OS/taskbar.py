import sys
import datetime
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
import theme
import animations

class SigeonTaskbar(QFrame):
    # Signals
    start_triggered = pyqtSignal()
    app_triggered = pyqtSignal(str) # App ID

    def __init__(self, parent_desktop=None):
        super().__init__(parent_desktop)
        self.desktop = parent_desktop
        self.init_ui()

    def init_ui(self):
        self.setObjectName("taskbar_frame")
        self.setFixedHeight(48)
        self.setStyleSheet(theme.get_stylesheet())
        
        # Layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)
        
        # 1. Left Side: Brand "Sigeon OS" button
        self.brand_widget = QWidget(self)
        self.brand_lay = QHBoxLayout(self.brand_widget)
        self.brand_lay.setContentsMargins(0, 0, 0, 0)
        self.brand_lay.setSpacing(4)
        
        self.btn_start = QPushButton(self.brand_widget)
        self.btn_start.setObjectName("taskbar_pigeon_btn")
        self.btn_start.setStyleSheet(theme.get_stylesheet())
        
        # Logo Icon + text
        self.start_ico = QLabel(self.btn_start)
        self.start_ico.setPixmap(theme.IconFactory.get_icon("wing_white", 20).pixmap(20, 20))
        
        self.start_txt = QLabel("Sigeon OS", self.btn_start)
        self.start_txt.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI', Arial; font-size: 13px;")
        
        # Assemble inner layout of button
        inner_lay = QHBoxLayout(self.btn_start)
        inner_lay.setContentsMargins(6, 4, 6, 4)
        inner_lay.setSpacing(6)
        inner_lay.addWidget(self.start_ico)
        inner_lay.addWidget(self.start_txt)
        
        self.btn_start.clicked.connect(self.on_start_clicked)
        self.brand_lay.addWidget(self.btn_start)
        self.layout.addWidget(self.brand_widget)
        
        # 2. Center: Pinned Apps Container
        self.apps_container = QWidget(self)
        self.apps_layout = QHBoxLayout(self.apps_container)
        self.apps_layout.setContentsMargins(0, 0, 0, 0)
        self.apps_layout.setSpacing(2)
        
        # List of pinned apps
        self.pinned_apps = [
            ("explorer", "folder"),
            ("paint", "photos"),
            ("flappy_game", "logo"),
            ("calendar", "calendar"),
            ("photos", "photos"),
            ("settings", "settings"),
            ("notepad", "notepad"),
            ("terminal", "terminal"),
            ("weather", "weather")
        ]
        
        self.app_buttons = {}
        
        for app_id, icon_name in self.pinned_apps:
            btn = QPushButton(self.apps_container)
            btn.setObjectName("taskbar_app_btn")
            btn.setStyleSheet(theme.get_stylesheet())
            btn.setFixedSize(36, 36)
            btn.setIcon(theme.IconFactory.get_icon(icon_name, 24))
            btn.setIconSize(QSize(24, 24))
            
            # Click connection
            btn.clicked.connect(lambda checked, a_id=app_id, b=btn: self.on_app_clicked(a_id, b))
            
            self.apps_layout.addWidget(btn)
            self.app_buttons[app_id] = btn
            
        self.layout.addWidget(self.apps_container, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 3. Right Side: System Tray
        self.tray = QWidget(self)
        self.tray_lay = QHBoxLayout(self.tray)
        self.tray_lay.setContentsMargins(0, 0, 0, 0)
        self.tray_lay.setSpacing(10)
        
        # Signal / Battery / Volume icons (Using clean Unicode symbols for high compatibility)
        self.tray_icons = QLabel("📶  🔋  🔊", self.tray)
        self.tray_icons.setStyleSheet("color: #ffffff; font-size: 13px;")
        self.tray_lay.addWidget(self.tray_icons)
        
        # Time / Date stacked vertically
        self.time_container = QWidget(self.tray)
        self.time_lay = QVBoxLayout(self.time_container)
        self.time_lay.setContentsMargins(0, 4, 0, 4)
        self.time_lay.setSpacing(0)
        
        self.lbl_time = QLabel("10:24 AM", self.time_container)
        self.lbl_time.setStyleSheet("color: #ffffff; font-size: 10px; font-weight: bold; font-family: 'Segoe UI', Arial;")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.lbl_date = QLabel("5/20/2024", self.time_container)
        self.lbl_date.setStyleSheet("color: #7f8c8d; font-size: 9px; font-family: 'Segoe UI', Arial;")
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.time_lay.addWidget(self.lbl_time)
        self.time_lay.addWidget(self.lbl_date)
        self.tray_lay.addWidget(self.time_container)
        
        self.layout.addWidget(self.tray)
        
        # Start Clock Timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock() # Initial sync

    def update_clock(self):
        now = datetime.datetime.now()
        # Display matching the photo format e.g. "10:24 AM" and "5/20/2024"
        self.lbl_time.setText(now.strftime("%I:%M %p"))
        self.lbl_date.setText(now.strftime("%m/%d/%Y"))

    # Highlight active app
    def set_app_active(self, app_id, is_active):
        if app_id in self.app_buttons:
            btn = self.app_buttons[app_id]
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().polish(btn)

    def on_start_clicked(self):
        animations.bounce(self.btn_start, duration=350)
        self.start_triggered.emit()

    def on_app_clicked(self, app_id, button):
        animations.bounce(button, duration=350)
        self.app_triggered.emit(app_id)
