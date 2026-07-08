import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint, QPointF, QSize, QDateTime
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush
import theme
import animations
from apps.users import load_users

class SigeonLoginScreen(QWidget):
    # Signal emitted when password is correct
    login_successful = pyqtSignal(str) # Emits the name of the logged in user

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shake_index = 0
        self.shake_offsets = [12, -12, 8, -8, 4, -4, 0]
        self.active_user = "Sky Pigeon"
        self.users = {}
        
        self.init_ui()
        self.reload_users()
        
        # Setup live clock timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

    def update_clock(self):
        now = QDateTime.currentDateTime()
        self.time_lbl.setText(now.toString("hh:mm"))
        self.date_lbl.setText(now.toString("dddd, MMMM d"))

    def reload_users(self):
        self.users = load_users()
        if self.users:
            if not hasattr(self, 'active_user') or self.active_user not in self.users:
                self.active_user = list(self.users.keys())[0]
        else:
            self.active_user = "Sky Pigeon"
            
        self.update_active_user_ui()
        self.update_other_users_ui()
        self.reset_elements_for_animation()

    def update_active_user_ui(self):
        self.user_lbl.setText(self.active_user)
        self.pass_input.setEnabled(True)
        self.btn_signin.setEnabled(True)
        self.pass_input.clear()
        self.status_lbl.setText("")

    def update_other_users_ui(self):
        # Clear layout
        while self.other_users_lay.count():
            item = self.other_users_lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        other_count = 0
        for username in self.users:
            if username == self.active_user:
                continue
                
            other_count += 1
            
            # Account widget container
            user_container = QWidget(self.other_users_widget)
            user_container.setCursor(Qt.CursorShape.PointingHandCursor)
            container_layout = QVBoxLayout(user_container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(6)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Rounded button icon
            avatar_btn = QPushButton(user_container)
            avatar_btn.setFixedSize(54, 54)
            avatar_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.08);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 27px;
                }
                QPushButton:hover {
                    border-color: #0f82df;
                    background-color: rgba(255, 255, 255, 0.18);
                }
            """)
            avatar_btn.setIcon(theme.IconFactory.get_icon("logo_white", 32))
            avatar_btn.setIconSize(QSize(32, 32))
            
            name_lbl = QLabel(username, user_container)
            name_lbl.setStyleSheet("color: white; font-size: 11px; font-weight: bold; background: transparent;")
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            container_layout.addWidget(avatar_btn)
            container_layout.addWidget(name_lbl)
            
            avatar_btn.clicked.connect(lambda checked, u=username: self.switch_user(u))
            self.other_users_lay.addWidget(user_container)

        self.other_users_widget.setVisible(other_count > 0)

    def switch_user(self, username):
        def finish_switch():
            self.active_user = username
            self.update_active_user_ui()
            self.update_other_users_ui()
            animations.fade_in(self.login_card, duration=300)
            
        animations.fade_out(self.login_card, duration=200, callback=finish_switch)

    def reset_elements_for_animation(self):
        widgets = [self.time_widget, self.login_card, self.bottom_bar]
        for w in widgets:
            animations._ensure_opacity_effect(w).setOpacity(0.0)

    def start_appear_animation(self):
        self.reset_elements_for_animation()
        widgets = [self.time_widget, self.login_card, self.bottom_bar]
        animations.staggered_fade_in(widgets, per_item_duration=600, delay_between=150)
        animations.pulse_glow(self.avatar_lbl, duration=2000)

    def init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Lock Screen Clock Widget
        self.time_widget = QWidget(self)
        self.time_layout = QVBoxLayout(self.time_widget)
        self.time_layout.setContentsMargins(0, 50, 0, 0)
        self.time_layout.setSpacing(4)
        self.time_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.time_lbl = QLabel(self.time_widget)
        self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_lbl.setStyleSheet("color: white; font-size: 72px; font-weight: 200; font-family: 'Segoe UI Light', 'Helvetica Neue', Arial; background: transparent;")
        
        self.date_lbl = QLabel(self.time_widget)
        self.date_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 18px; font-weight: 400; font-family: 'Segoe UI', Arial; background: transparent;")
        
        self.time_layout.addWidget(self.time_lbl)
        self.time_layout.addWidget(self.date_lbl)
        self.main_layout.addWidget(self.time_widget)
        
        # 2. Frosted Glass Central Container
        self.center_frame = QWidget(self)
        self.center_lay = QVBoxLayout(self.center_frame)
        self.center_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Glassmorphic Login Card
        self.login_card = QFrame(self.center_frame)
        self.login_card.setObjectName("login_card")
        self.login_card.setStyleSheet("""
            QFrame#login_card {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 16px;
            }
        """)
        self.card_layout = QVBoxLayout(self.login_card)
        self.card_layout.setContentsMargins(35, 35, 35, 35)
        self.card_layout.setSpacing(15)
        self.card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Profile avatar
        self.avatar_lbl = QLabel(self.login_card)
        self.avatar_lbl.setPixmap(theme.IconFactory.get_icon("logo", 96).pixmap(96, 96))
        self.avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_lbl.setFixedSize(96, 96)
        self.avatar_lbl.setStyleSheet("""
            border-radius: 48px;
            border: 2px solid rgba(255, 255, 255, 0.35);
            background-color: rgba(255, 255, 255, 0.08);
        """)
        self.card_layout.addWidget(self.avatar_lbl)
        
        # Username
        self.user_lbl = QLabel("Sky Pigeon", self.login_card)
        self.user_lbl.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold; font-family: 'Segoe UI', Arial; background: transparent;")
        self.user_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_layout.addWidget(self.user_lbl)
        
        # Input Form Container (for shaking)
        self.form_widget = QWidget(self.login_card)
        self.form_layout = QHBoxLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(6)
        
        # Password Input
        self.pass_input = QLineEdit(self.form_widget)
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setFixedWidth(200)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: white;
                padding: 7px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid #0f82df;
            }
        """)
        self.pass_input.returnPressed.connect(self.attempt_login)
        self.form_layout.addWidget(self.pass_input)
        
        # Sign In Button
        self.btn_signin = QPushButton("→", self.form_widget)
        self.btn_signin.setFixedSize(30, 30)
        self.btn_signin.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0f82df;
                border-color: #0f82df;
            }
        """)
        self.btn_signin.clicked.connect(self.attempt_login)
        self.form_layout.addWidget(self.btn_signin)
        self.card_layout.addWidget(self.form_widget)
        
        # Status Label (errors, loading)
        self.status_lbl = QLabel("", self.login_card)
        self.status_lbl.setStyleSheet("color: #ff4a4a; font-size: 11px; font-weight: 500; background: transparent;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_layout.addWidget(self.status_lbl)
        
        self.center_lay.addWidget(self.login_card)
        self.main_layout.addWidget(self.center_frame, stretch=1)
        
        # 3. Bottom controls overlay
        self.bottom_bar = QWidget(self)
        self.bottom_bar.setFixedHeight(80)
        self.bottom_lay = QHBoxLayout(self.bottom_bar)
        self.bottom_lay.setContentsMargins(40, 0, 40, 20)
        
        # Bottom-Center: Other accounts list
        self.other_users_widget = QWidget(self.bottom_bar)
        self.other_users_lay = QHBoxLayout(self.other_users_widget)
        self.other_users_lay.setContentsMargins(0, 0, 0, 0)
        self.other_users_lay.setSpacing(24)
        self.bottom_lay.addWidget(self.other_users_widget, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        
        self.bottom_lay.addStretch()
        
        # Bottom-Right tray
        tray_container = QWidget(self.bottom_bar)
        tray_lay = QHBoxLayout(tray_container)
        tray_lay.setContentsMargins(0, 0, 0, 0)
        tray_lay.setSpacing(15)
        
        self.tray_icons = QLabel("📶  🔋", tray_container)
        self.tray_icons.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 15px; background: transparent;")
        tray_lay.addWidget(self.tray_icons, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Power Button
        self.btn_power = QPushButton("⏻", tray_container)
        self.btn_power.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 20px;
            }
            QPushButton:hover {
                color: #ff4a4a;
            }
        """)
        self.btn_power.clicked.connect(self.shutdown)
        tray_lay.addWidget(self.btn_power, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        self.bottom_lay.addWidget(tray_container, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.bottom_bar)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Beautiful dynamic wallpaper gradient (magenta to royal purple to navy space blue)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#b33939")) # Warm deep red
        grad.setColorAt(0.4, QColor("#482ff7")) # Royal violet-blue
        grad.setColorAt(1.0, QColor("#0c1033")) # Deep space navy
        
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())
        
        # Draw translucent glowing aesthetic circles
        painter.setBrush(QBrush(QColor("rgba(255, 255, 255, 0.03)")))
        painter.drawEllipse(QPointF(self.width() * 0.15, self.height() * 0.25), self.height() * 0.35, self.height() * 0.35)
        painter.drawEllipse(QPointF(self.width() * 0.85, self.height() * 0.75), self.height() * 0.45, self.height() * 0.45)

    def attempt_login(self):
        entered_pass = self.pass_input.text().strip()
        correct_pass = self.users.get(self.active_user)
        
        if correct_pass is not None and entered_pass == correct_pass:
            self.status_lbl.setStyleSheet("color: #2ec27e; font-size: 11px; background: transparent;")
            self.status_lbl.setText("Welcome...")
            self.pass_input.setEnabled(False)
            self.btn_signin.setEnabled(False)
            
            animations.stop_pulse(self.avatar_lbl)
            
            self.login_timer = QTimer(self)
            self.login_timer.timeout.connect(self.finish_login)
            self.login_timer.start(800)
        else:
            self.status_lbl.setStyleSheet("color: #ff4a4a; font-size: 11px; background: transparent;")
            self.status_lbl.setText("Incorrect password. Try again.")
            self.start_shake()
            self.pass_input.clear()

    def start_shake(self):
        self.shake_index = 0
        self.shake_timer = QTimer(self)
        self.shake_timer.timeout.connect(self.do_shake)
        self.shake_timer.start(40)

    def do_shake(self):
        if self.shake_index < len(self.shake_offsets):
            offset = self.shake_offsets[self.shake_index]
            self.form_layout.setContentsMargins(10 + offset, 0, 10 - offset, 0)
            self.shake_index += 1
        else:
            self.shake_timer.stop()
            self.form_layout.setContentsMargins(0, 0, 0, 0)

    def finish_login(self):
        self.login_timer.stop()
        self.login_successful.emit(self.active_user)

    def reset(self):
        self.pass_input.clear()
        self.status_lbl.setText("")
        self.pass_input.setEnabled(True)
        self.btn_signin.setEnabled(True)
        self.reload_users()
        self.reset_elements_for_animation()

    def shutdown(self):
        sys.exit(0)
