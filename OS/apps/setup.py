import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import theme
import animations
from apps.users import save_users, load_users

class SigeonSetupScreen(QWidget):
    setup_completed = pyqtSignal(str) # Emits the name of the created user

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Center Container
        self.center_frame = QFrame(self)
        self.center_frame.setObjectName("setup_container_card")
        self.center_frame.setFixedSize(380, 420)
        self.center_frame.setStyleSheet("""
            QFrame#setup_container_card {
                background-color: rgba(20, 28, 45, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 16px;
            }
        """)

        # Add shadow to container
        animations.add_drop_shadow(self.center_frame, blur=25, offset_x=0, offset_y=6)

        self.center_lay = QVBoxLayout(self.center_frame)
        self.center_lay.setContentsMargins(30, 24, 30, 24)
        self.center_lay.setSpacing(14)
        self.center_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo Icon
        self.logo_lbl = QLabel(self.center_frame)
        self.logo_lbl.setPixmap(theme.IconFactory.get_icon("logo", 72).pixmap(72, 72))
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lay.addWidget(self.logo_lbl)

        # Welcome Title
        self.title_lbl = QLabel("Welcome to SigeonOS", self.center_frame)
        self.title_lbl.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold; font-family: 'Segoe UI', Arial;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lay.addWidget(self.title_lbl)

        self.subtitle_lbl = QLabel("Create your administrator account to get started.", self.center_frame)
        self.subtitle_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 11px; margin-bottom: 6px;")
        self.subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_lbl.setWordWrap(True)
        self.center_lay.addWidget(self.subtitle_lbl)

        # Username Input
        self.user_input = QLineEdit(self.center_frame)
        self.user_input.setPlaceholderText("Username (e.g. SkyPigeon)")
        self.user_input.setStyleSheet(self.get_input_style())
        self.center_lay.addWidget(self.user_input)

        # Password Input
        self.pass_input = QLineEdit(self.center_frame)
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet(self.get_input_style())
        self.center_lay.addWidget(self.pass_input)

        # Confirm Password Input
        self.confirm_input = QLineEdit(self.center_frame)
        self.confirm_input.setPlaceholderText("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setStyleSheet(self.get_input_style())
        self.center_lay.addWidget(self.confirm_input)

        # Status Label (Errors)
        self.status_lbl = QLabel("", self.center_frame)
        self.status_lbl.setStyleSheet("color: #ff5e5e; font-size: 11px; font-weight: 500;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lay.addWidget(self.status_lbl)

        # Create Button
        self.btn_create = QPushButton("Create Account →", self.center_frame)
        self.btn_create.setFixedHeight(36)
        self.btn_create.setStyleSheet("""
            QPushButton {
                background-color: #0f82df;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3fa5fc;
            }
            QPushButton:pressed {
                background-color: #0c6cbd;
            }
        """)
        self.btn_create.clicked.connect(self.create_account)
        self.center_lay.addWidget(self.btn_create)

        # Add layout centered in window
        outer_layout = QHBoxLayout()
        outer_layout.addStretch()
        outer_layout.addWidget(self.center_frame)
        outer_layout.addStretch()

        self.main_layout.addStretch()
        self.main_layout.addLayout(outer_layout)
        self.main_layout.addStretch()

        # Keyboard shortcuts
        self.confirm_input.returnPressed.connect(self.create_account)

    def get_input_style(self):
        return """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                color: white;
                padding: 6px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid #0f82df;
            }
        """

    def paintEvent(self, event):
        painter = theme.QPainter(self)
        painter.setRenderHint(theme.QPainter.RenderHint.Antialiasing)
        
        # Deep blue background gradient
        grad = theme.QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, theme.QColor("#101b2f"))
        grad.setColorAt(1, theme.QColor("#080d17"))
        
        painter.setBrush(theme.QBrush(grad))
        painter.setPen(theme.Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())
        
        # Soft wing glow background
        painter.setBrush(theme.QBrush(theme.QColor("rgba(255, 255, 255, 0.02)")))
        painter.drawEllipse(theme.QPointF(self.width()/2, self.height()/2), self.height()*0.4, self.height()*0.4)

    def create_account(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text()
        confirm = self.confirm_input.text()

        if not username:
            self.status_lbl.setText("Please enter a username.")
            return
        if len(password) < 3:
            self.status_lbl.setText("Password must be at least 3 characters.")
            return
        if password != confirm:
            self.status_lbl.setText("Passwords do not match.")
            return

        # Load existing users
        users = load_users()
        if username.lower() in [u.lower() for u in users.keys()]:
            self.status_lbl.setText("Username already exists.")
            return

        # Save user
        users[username] = password
        if save_users(users):
            self.status_lbl.setStyleSheet("color: #2ec27e; font-size: 11px;")
            self.status_lbl.setText("Account created successfully!")
            self.btn_create.setEnabled(False)
            
            # Transition delay
            QTimer.singleShot(1000, lambda: self.setup_completed.emit(username))
        else:
            self.status_lbl.setText("Failed to save user account.")
