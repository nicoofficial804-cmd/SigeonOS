import sys
import os
import re
import traceback
import time
import platform
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QStackedWidget, QFrame
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QBrush, QPen, QPainterPath
import theme

class SadPigeonWidget(QWidget):
    print("!!CRASH!!")
    """Draws Sigeon's pigeon logo in white with blue features matching the BSOD reference photo"""
    def __init__(self, parent=None, size=160, color=QColor("#0a5bc2")):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.color = color
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        w = float(self.width())
        # Scale to fit (logo path is roughly 34x32)
        scale = w / 55.0
        
        # Draw the main pigeon silhouette in solid white
        path = QPainterPath()
        path.moveTo(10, 32)
        path.lineTo(2, 32)
        path.lineTo(6, 25)
        path.quadTo(15, 18, 22, 18)
        path.lineTo(24, 12)
        path.arcTo(20, 4, 12, 12, -45, 180)
        path.lineTo(34, 11)
        path.lineTo(31, 14)
        path.quadTo(24, 20, 25, 28)
        path.quadTo(20, 34, 10, 32)
        
        painter.save()
        painter.scale(scale, scale)
        
        # Fill pigeon body with white
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Now, draw the features in the BSOD background color (acting as cutouts)
        painter.setPen(QPen(self.color, 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Neck line (collar)
        neck_path = QPainterPath()
        neck_path.moveTo(23.5, 19.5)
        neck_path.quadTo(21.5, 22.0, 19.5, 23.5)
        painter.drawPath(neck_path)
        
        # Wing outline curve
        wing = QPainterPath()
        wing.moveTo(14, 21)
        wing.quadTo(21, 21, 23, 26)
        wing.quadTo(18, 31, 11, 26)
        wing.lineTo(14, 21)
        painter.drawPath(wing)
        
        # Eye: Blue circle containing a white cross 'X'
        eye_rect = QRectF(26.0, 7.0, 3.5, 3.5)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(eye_rect)
        
        # White X inside the eye
        painter.setPen(QPen(Qt.GlobalColor.white, 0.6))
        painter.drawLine(QPointF(26.8, 7.8), QPointF(28.7, 9.7))
        painter.drawLine(QPointF(28.7, 7.8), QPointF(26.8, 9.7))
        
        # Blue teardrop falling from the eye
        teardrop = QPainterPath()
        teardrop.moveTo(27.8, 11.0)
        teardrop.quadTo(26.5, 13.0, 27.8, 14.2)
        teardrop.quadTo(29.1, 13.0, 27.8, 11.0)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(teardrop)
        
        painter.restore()

class QRCodeWidget(QWidget):
    """Draws a vector blue-and-white QR code matching the BSOD visual reference"""
    def __init__(self, parent=None, size=150, color=QColor("#0a5bc2")):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.color = color
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False) # Sharp square blocks
        
        # White background square
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())
        
        # Grid layout (21x21 modules)
        grid_size = 21
        cell_size = self.width() / grid_size
        
        # Draw position detection markers in the corners
        def draw_position_marker(gx, gy):
            # Outer 7x7
            painter.setBrush(QBrush(self.color))
            painter.drawRect(QRectF(gx * cell_size, gy * cell_size, 7 * cell_size, 7 * cell_size))
            # Inner 5x5 white
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            painter.drawRect(QRectF((gx + 1) * cell_size, (gy + 1) * cell_size, 5 * cell_size, 5 * cell_size))
            # Center 3x3 blue
            painter.setBrush(QBrush(self.color))
            painter.drawRect(QRectF((gx + 2) * cell_size, (gy + 2) * cell_size, 3 * cell_size, 3 * cell_size))
            
        draw_position_marker(0, 0)   # Top-left
        draw_position_marker(14, 0)  # Top-right
        draw_position_marker(0, 14)  # Bottom-left
        
        # Generate random modules elsewhere (using a stable seed so it doesn't animate/flicker)
        import random
        random.seed(1337)
        
        painter.setBrush(QBrush(self.color))
        for x in range(grid_size):
            for y in range(grid_size):
                # Skip position markers area
                if (x < 8 and y < 8) or (x >= 13 and y < 8) or (x < 8 and y >= 13):
                    continue
                # 45% module density
                if random.random() < 0.45:
                    painter.drawRect(QRectF(x * cell_size, y * cell_size, cell_size, cell_size))

class BSODScreen(QMainWindow):
    """Full-screen BSOD crash screen for SigeonOS matching the user's reference photo"""
    def __init__(self, stop_code, tb_text, failing_file, main_window=None):
        super().__init__()
        self.setObjectName("BSODScreen")
        self.setWindowTitle("Sigeon OS - Crash")
        self.stop_code = stop_code
        self.tb_text = tb_text
        self.failing_file = failing_file
        self.main_window = main_window
        
        # Fullscreen borderless window staying on top
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        screen = self.screen().geometry()
        self.setGeometry(screen)
        
        self.init_ui()
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        
    def init_ui(self):
        # We use a Stacked Widget for the main layout to easily toggle debug view
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # Page 0: Beautiful BSOD Screen
        bsod_page = QWidget()
        bsod_page.setStyleSheet("background-color: #0a5bc2; color: white;")
        bsod_layout = QVBoxLayout(bsod_page)
        bsod_layout.setContentsMargins(80, 80, 80, 40)
        bsod_layout.setSpacing(0)
        
        # 1. Top Section (Pigeon and Main Message)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(40)
        
        # Vector Sad Pigeon Icon
        self.pigeon_widget = SadPigeonWidget(self, size=150, color=QColor("#0a5bc2"))
        top_layout.addWidget(self.pigeon_widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Main text details
        text_layout = QVBoxLayout()
        text_layout.setSpacing(15)
        
        title_label = QLabel("Oh no! Sigeon OS ran into a problem and needs to restart.")
        title_font = QFont("Segoe UI", 26)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; background: transparent;")
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)
        
        subtitle_label = QLabel("We're sorry about that. Your pigeon was doing important things.")
        subtitle_font = QFont("Segoe UI", 13)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.95); background: transparent;")
        subtitle_label.setWordWrap(True)
        text_layout.addWidget(subtitle_label)
        
        # Progress Counter
        self.progress_percent = 0
        self.progress_label = QLabel("0% complete")
        self.progress_label.setFont(subtitle_font)
        self.progress_label.setStyleSheet("color: rgba(255, 255, 255, 0.95); background: transparent;")
        text_layout.addWidget(self.progress_label)
        
        top_layout.addLayout(text_layout, stretch=1)
        bsod_layout.addLayout(top_layout)
        # Push everything to the top to leave room for the footer
        bsod_layout.addStretch()
        
        # 3. Bottom Section (Separator line and Sigeon OS Footer)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.15); max-height: 1px; border: none;")
        bsod_layout.addWidget(separator)
        bsod_layout.addSpacing(20)
        
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(20)
        
        # Logo on left (using HTML for OS box styling)
        branding_lbl = QLabel()
        branding_lbl.setText(
            '<span style="font-family: \'Segoe UI\'; font-weight: bold; font-size: 15px; color: white;">Sigeon</span>'
            '&nbsp;'
            '<span style="font-family: \'Segoe UI\'; border: 1.2px solid white; border-radius: 4px; padding: 1px 5px; font-weight: bold; font-size: 10px; color: white;">OS</span>'
        )
        branding_lbl.setStyleSheet("background: transparent;")
        footer_layout.addWidget(branding_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Vertical divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.15); max-width: 1px; min-height: 30px; border: none;")
        footer_layout.addWidget(divider, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Version details on right
        ver_lbl = QLabel("Sigeon OS 1.0.0 (Blue Feather Update)\nKeeping the sky smooth and the cooing strong. 🕊")
        ver_font = QFont("Segoe UI", 9)
        ver_lbl.setFont(ver_font)
        ver_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.7); background: transparent; line-height: 1.3;")
        footer_layout.addWidget(ver_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        footer_layout.addStretch()
        bsod_layout.addLayout(footer_layout)
        
        self.stacked_widget.addWidget(bsod_page)
        
        # Page 1: Traceback Debug Terminal view
        self.debug_text_area = QTextEdit()
        self.debug_text_area.setReadOnly(True)
        self.debug_text_area.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: none;
                padding: 20px;
            }
        """)
        
        # Format diagnostic message
        debug_msg = (
            "================================================================================\n"
            "                        SIGEONOS DIAGNOSTIC CRASH REPORT                        \n"
            "================================================================================\n\n"
            f"STOP CODE: {self.stop_code}\n"
            f"WHAT FAILED: {self.failing_file}\n"
            f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "PYTHON TRACEBACK DETAILS:\n"
            "--------------------------------------------------------------------------------\n"
            f"{self.tb_text}\n"
            "--------------------------------------------------------------------------------\n\n"
            "Press ENTER to REBOOT the computer (Windows/Linux).\n"
            "Press ESCAPE to return to the crash screen."
        )
        self.debug_text_area.setText(debug_msg)
        
        self.stacked_widget.addWidget(self.debug_text_area)
        
        # Setup progress timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_progress)
        self.animation_timer.start(80) # Increments 1% every 80ms (~8 seconds total)

    def update_progress(self):
        self.progress_percent += 1
        if self.progress_percent > 100:
            self.progress_percent = 100
            self.animation_timer.stop()
            # Wait 1 second at 100%, then reboot
            QTimer.singleShot(1000, self.trigger_reboot)
        self.progress_label.setText(f"{self.progress_percent}% complete")
        
    def trigger_reboot(self):
        self.animation_timer.stop()
        self.reboot_host_pc()
            
    def toggle_debug_view(self):
        if self.stacked_widget.currentIndex() == 0:
            # Entering debug view -> stop the progress timer to pause progress and disable auto-reboot
            self.animation_timer.stop()
            self.stacked_widget.setCurrentIndex(1)
            self.debug_text_area.setFocus()
        else:
            # Returning to BSOD screen -> keep timer stopped so it remains frozen
            self.stacked_widget.setCurrentIndex(0)
            self.setFocus()

    def reboot_host_pc(self):
        # Reboot actual physical host machine, unless in test mode
        if "--test-mode" in sys.argv:
            print("[Test Mode] Host PC reboot command bypassed.")
            # For test mode in GUI emulator, just close the window
            self.close()
            if self.main_window:
                self.main_window.show()
                self.main_window.reboot()
            else:
                sys.exit(0)
            return
            
        sys_name = platform.system()
        if sys_name == "Windows":
            os.system("shutdown /r /t 1")
        else:
            # Linux, macOS, etc.
            os.system("reboot")

    def keyPressEvent(self, event):
        key_text = event.text().upper()
        
        # If in debug traceback view (index 1), handle key events
        if self.stacked_widget.currentIndex() == 1:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                # Trigger physical host PC reboot immediately!
                self.reboot_host_pc()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Escape:
                # Escape returns to BSOD screen
                self.toggle_debug_view()
                event.accept()
                return
                
        # Handle the secret DEBUG sequence to open debug view
        if key_text:
            now = time.time()
            if not hasattr(self, 'last_key_time'):
                self.last_key_time = 0
                self.debug_buffer = ""
            
            # Reset buffer on 5 seconds inactivity
            if now - self.last_key_time > 5.0:
                self.debug_buffer = ""
                
            self.last_key_time = now
            self.debug_buffer += key_text
            self.debug_buffer = self.debug_buffer[-5:]
            
            if self.debug_buffer == "DEBUG":
                self.debug_buffer = ""
                self.toggle_debug_view()
                
        super().keyPressEvent(event)

def setup_crash_handler(app):
    """Sets up a robust sys.excepthook to display the custom BSOD screen"""
    
    def custom_excepthook(exc_type, exc_value, exc_traceback):
        # Format the full traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)
        
        # Always output to standard error for console logs
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
        # 1. Stop Code: derive from exception class name (e.g. ZeroDivisionError -> ZERO_DIVISION_ERROR)
        class_name = exc_type.__name__
        stop_code = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).upper()
        
        # 2. What Failed: extract base name of the last frame inside our application
        failing_file = "feather.sys"
        tb = exc_traceback
        while tb is not None:
            frame = tb.tb_frame
            filename = frame.f_code.co_filename
            base_name = os.path.basename(filename)
            if base_name.endswith('.py') and not filename.startswith('<'):
                failing_file = base_name
            tb = tb.tb_next
            
        # Overwrite info to exactly match the reference photo if it's the desktop manual crash sequence
        if "Manual crash triggered" in str(exc_value):
            stop_code = "C00-C00-CRASH"
            failing_file = "feather.sys"
            
        # Hide all visible top-level windows of the application
        main_win = None
        for widget in app.topLevelWidgets():
            if widget.isVisible() and widget.objectName() != "BSODScreen":
                if hasattr(widget, 'stacked_widget'):
                    main_win = widget
                widget.hide()
                
        # Instantiate and show BSOD Screen
        global bsod_instance
        bsod_instance = BSODScreen(stop_code, tb_text, failing_file, main_win)
        bsod_instance.show()
        
        # Pump event loop several times to force drawing
        for _ in range(10):
            app.processEvents()
            
    sys.excepthook = custom_excepthook
