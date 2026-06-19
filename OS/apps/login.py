import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint, QSize
from PyQt6.QtGui import QFont
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

    def reload_users(self):
        self.users = load_users()
        # Set active user to the first one available
        if self.users:
            # Keep active user if still in dict, otherwise select first
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

        # Add other users as small clickable buttons
        other_count = 0
        for username in self.users:
            if username == self.active_user:
                continue
                
            other_count += 1
            btn = QPushButton(self.other_users_widget)
            btn.setObjectName("other_user_btn")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 6px;
                    color: white;
                    padding: 4px 10px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.18);
                    border: 1px solid #0f82df;
                }
            """)
            
            lay = QHBoxLayout(btn)
            lay.setContentsMargins(4, 2, 4, 2)
            lay.setSpacing(6)
            
            ico = QLabel(btn)
            ico.setPixmap(theme.IconFactory.get_icon("logo_white", 14).pixmap(14, 14))
            lbl = QLabel(username, btn)
            lbl.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
            
            lay.addWidget(ico)
            lay.addWidget(lbl)
            
            # Switch connection
            btn.clicked.connect(lambda checked, u=username: self.switch_user(u))
            self.other_users_lay.addWidget(btn)

        self.other_users_widget.setVisible(other_count > 0)

    def switch_user(self, username):
        def finish_switch():
            self.active_user = username
            self.update_active_user_ui()
            self.update_other_users_ui()
            animations.fade_in(self.center_frame, duration=300)
            
        animations.fade_out(self.center_frame, duration=200, callback=finish_switch)

    def reset_elements_for_animation(self):
        widgets = [self.avatar_lbl, self.user_lbl, self.form_widget, self.bottom_bar]
        for w in widgets:
            animations._ensure_opacity_effect(w).setOpacity(0.0)

    def start_appear_animation(self):
        self.reset_elements_for_animation()
        widgets = [self.avatar_lbl, self.user_lbl, self.form_widget, self.bottom_bar]
        animations.staggered_fade_in(widgets, per_item_duration=600, delay_between=150)
        animations.pulse_glow(self.avatar_lbl, duration=2000)

    def init_ui(self):
        # Layouts
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Center container
        self.center_frame = QWidget(self)
        self.center_lay = QVBoxLayout(self.center_frame)
        self.center_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lay.setSpacing(14)
        
        # Profile avatar (Circular blue logo with pigeon)
        self.avatar_lbl = QLabel(self.center_frame)
        self.avatar_lbl.setPixmap(theme.IconFactory.get_icon("logo", 96).pixmap(96, 96))
        self.avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lay.addWidget(self.avatar_lbl)
        
        # Username
        self.user_lbl = QLabel("Sky Pigeon", self.center_frame)
        self.user_lbl.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Segoe UI', Arial;")
        self.user_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lay.addWidget(self.user_lbl)
        
        # Input Form Container (for shaking)
        self.form_widget = QWidget(self.center_frame)
        self.form_layout = QHBoxLayout(self.form_widget)
        self.form_layout.setContentsMargins(10, 0, 10, 0)
        self.form_layout.setSpacing(6)
        
        # Password Input
        self.pass_input = QLineEdit(self.form_widget)
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setFixedWidth(200)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 6px;
                color: white;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.25);
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
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
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
        
        self.center_lay.addWidget(self.form_widget)
        
        # Status Label (errors, loading)
        self.status_lbl = QLabel("", self.center_frame)
        
        # Status Label (errors, loading)
        self.status_lbl = QLabel("", self.center_frame)
        self.status_lbl.setStyleSheet("color: #ff4a4a; font-size: 11px; font-weight: 500;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lay.addWidget(self.status_lbl)
        
        self.main_layout.addWidget(self.center_frame, stretch=1)
        
        # Bottom controls overlay (Tray buttons: Power, Wi-Fi, Accessibility, Other Users)
        self.bottom_bar = QWidget(self)
        self.bottom_bar.setFixedHeight(50)
        self.bottom_lay = QHBoxLayout(self.bottom_bar)
        self.bottom_lay.setContentsMargins(20, 0, 20, 10)
        
        # Bottom-Left: Other accounts list container
        self.other_users_widget = QWidget(self.bottom_bar)
        self.other_users_lay = QHBoxLayout(self.other_users_widget)
        self.other_users_lay.setContentsMargins(0, 0, 0, 0)
        self.other_users_lay.setSpacing(8)
        self.bottom_lay.addWidget(self.other_users_widget)
        
        self.bottom_lay.addStretch()
        
        # Tray Labels
        self.tray_icons = QLabel("📶  🔋", self.bottom_bar)
        self.tray_icons.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 14px; margin-right: 10px;")
        self.bottom_lay.addWidget(self.tray_icons)
        
        # Power Button
        self.btn_power = QPushButton("⏻", self.bottom_bar)
        self.btn_power.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 18px;
            }
            QPushButton:hover {
                color: #ff4a4a;
            }
        """)
        self.btn_power.clicked.connect(self.shutdown)
        self.bottom_lay.addWidget(self.btn_power)
        
        self.main_layout.addWidget(self.bottom_bar)

    def paintEvent(self, event):
        # Paint the full screen wallpaper gradient
        painter = theme.QPainter(self)
        painter.setRenderHint(theme.QPainter.RenderHint.Antialiasing)
        
        # Deep blue background gradient
        grad = theme.QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, theme.QColor("#1a2b4c"))
        grad.setColorAt(1, theme.QColor("#0b1424"))
        
        painter.setBrush(theme.QBrush(grad))
        painter.setPen(theme.Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())
        
        # Draw soft pigeon wing glow in the center background
        painter.setBrush(theme.QBrush(theme.QColor("rgba(255, 255, 255, 0.03)")))
        painter.drawEllipse(theme.QPointF(self.width()/2, self.height()/2), self.height()*0.4, self.height()*0.4)

    def attempt_login(self):
        entered_pass = self.pass_input.text().strip()
        correct_pass = self.users.get(self.active_user)
        
        if correct_pass is not None and entered_pass == correct_pass:
            self.status_lbl.setStyleSheet("color: #2ec27e; font-size: 11px;")
            self.status_lbl.setText("Welcome...")
            self.pass_input.setEnabled(False)
            self.btn_signin.setEnabled(False)
            
            # Stop the pulsing glow
            animations.stop_pulse(self.avatar_lbl)
            
            # Simple loading timer
            self.login_timer = QTimer(self)
            self.login_timer.timeout.connect(self.finish_login)
            self.login_timer.start(800)
        else:
            self.status_lbl.setStyleSheet("color: #ff4a4a; font-size: 11px;")
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
            self.form_layout.setContentsMargins(10, 0, 10, 0)

    def finish_login(self):
        self.login_timer.stop()
        self.login_successful.emit(self.active_user)

    def reset(self):
        """Reset the login UI to its initial state for a new login session."""
        # Clear password field and status label
        self.pass_input.clear()
        self.status_lbl.setText("")
        # Enable inputs
        self.pass_input.setEnabled(True)
        self.btn_signin.setEnabled(True)
        # Reload users (in case new users were added)
        self.reload_users()
        # Reset animation elements (so start animation works correctly)
        self.reset_elements_for_animation()
        # Optionally start appear animation (caller can decide)
        # self.start_appear_animation()

    def shutdown(self):
        sys.exit(0)
