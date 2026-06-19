import os
import random
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QSize, QTimer
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush, QLinearGradient, QMouseEvent
import theme
from window import SigeonWindow
from start_menu import SigeonStartMenu
import animations

# Import apps
from apps.explorer import SigeonExplorer
from apps.settings import SigeonSettings
from apps.terminal import SigeonTerminal
from apps.notepad import SigeonNotepad
from apps.paint import SigeonPaint
from apps.weather import SigeonWeather
from apps.photos import SigeonPhotos
from apps.flappy import FlappyPigeonGame
from apps.tty import SigeonTTY
from apps.fs import VirtualFile

class DesktopIcon(QWidget):
    def __init__(self, name, icon_name, app_id, desktop_parent, is_file=False, file_obj=None):
        super().__init__(desktop_parent)
        self.desktop = desktop_parent
        self.app_id = app_id
        self.is_file = is_file
        self.file_obj = file_obj
        self.name = name
        
        self.setFixedSize(72, 72)
        self.setObjectName("desktop_icon_btn")
        self.setStyleSheet("""
            QWidget#desktop_icon_btn {
                background: transparent;
                border-radius: 6px;
            }
            QWidget#desktop_icon_btn:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 4, 2, 4)
        lay.setSpacing(2)
        
        self.ico_lbl = QLabel(self)
        self.ico_lbl.setPixmap(theme.IconFactory.get_icon(icon_name, 36).pixmap(36, 36))
        self.ico_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.txt_lbl = QLabel(name, self)
        self.txt_lbl.setStyleSheet("color: white; font-size: 11px;")
        self.txt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_lbl.setWordWrap(True)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setOffset(1, 1)
        shadow.setColor(QColor(0, 0, 0, 220))
        self.txt_lbl.setGraphicsEffect(shadow)
        
        lay.addWidget(self.ico_lbl)
        lay.addWidget(self.txt_lbl)
        
        self._drag_start_pos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
            self.raise_()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_start_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.pos() - self._drag_start_pos
            if delta.manhattanLength() > 3:
                new_pos = self.mapToParent(event.pos() - self._drag_start_pos)
                self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._drag_start_pos is not None:
                delta = event.pos() - self._drag_start_pos
                self._drag_start_pos = None
                if delta.manhattanLength() <= 3:
                    # Click
                    animations.bounce(self, duration=350)
                    QTimer.singleShot(150, self.trigger)
                else:
                    # Dropped, save position
                    self.desktop.save_icon_positions()
        super().mouseReleaseEvent(event)
        
    def trigger(self):
        if self.is_file:
            self.desktop.open_file(self.name, self.file_obj)
        else:
            self.desktop.open_app(self.app_id)


class SigeonDesktop(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setObjectName("desktop_workspace")
        
        # Window Manager state
        self.open_windows = {} # app_id -> SigeonWindow
        self.stagger_count = 0
        self.wallpaper_type = "wallpaper" # wallpaper, dark, pink, green, orange
        
        # Load wallpaper pixmap
        self.wallpaper_pixmap = None
        wp_path = os.path.join(os.path.dirname(__file__), "assets", "wallpaper.png")
        if os.path.exists(wp_path):
            self.wallpaper_pixmap = QPixmap(wp_path)
            
        self.icon_widgets = []
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(theme.get_stylesheet())

    def load_desktop_icons(self):
        # Remove existing icons
        for w in self.icon_widgets:
            w.setParent(None)
            w.deleteLater()
        self.icon_widgets.clear()
        
        system_icons = [
            ("Pigeon", "logo", "about", False, None),
            ("Files", "folder", "explorer", False, None),
            ("Paint", "photos", "paint", False, None),
            ("Flappy Pigeon", "logo", "flappy_game", False, None),
            ("Settings", "settings", "settings", False, None),
            ("Terminal", "terminal", "terminal", False, None),
            ("Host TTY", "terminal", "tty", False, None),
            ("Recycle Bin", "recycle_empty", "recycle", False, None)
        ]
        
        # Load from Home/Desktop
        all_icons = list(system_icons)
        if self.main_window and self.main_window.fs:
            fs = self.main_window.fs
            desktop_node = fs.get_node(["Home", "Desktop"])
            if isinstance(desktop_node, dict):
                for fname, fobj in desktop_node.items():
                    if isinstance(fobj, VirtualFile):
                        icon_name = "file_" + fobj.file_type
                        all_icons.append((fname, icon_name, "file", True, fobj))
                        
        # Load saved positions
        saved_pos = {}
        if self.main_window and self.main_window.fs.current_user:
            cfg_path = os.path.join(self.main_window.fs.base_dir, "users", self.main_window.fs.current_user, "desktop.json")
            if os.path.exists(cfg_path):
                try:
                    with open(cfg_path, "r") as f:
                        saved_pos = json.load(f)
                except:
                    pass

        x = 20
        y = 20
        spacing = 86
        
        # Fallback to current size if possible, otherwise hardcoded default
        desk_height = self.height() if self.height() > 0 else 1080
        
        for name, icon_name, app_id, is_file, file_obj in all_icons:
            icon_w = DesktopIcon(name, icon_name, app_id, self, is_file, file_obj)
            
            key = app_id if not is_file else f"file_{name}"
            if key in saved_pos:
                icon_w.move(saved_pos[key][0], saved_pos[key][1])
            else:
                icon_w.move(x, y)
                y += spacing
                if y > desk_height - 100:
                    y = 20
                    x += spacing
                    
            icon_w.show()
            self.icon_widgets.append(icon_w)

    def save_icon_positions(self):
        if not self.main_window or not self.main_window.fs.current_user:
            return
        saved_pos = {}
        for w in self.icon_widgets:
            key = w.app_id if not w.is_file else f"file_{w.name}"
            saved_pos[key] = [w.x(), w.y()]
            
        cfg_path = os.path.join(self.main_window.fs.base_dir, "users", self.main_window.fs.current_user, "desktop.json")
        try:
            with open(cfg_path, "w") as f:
                json.dump(saved_pos, f)
        except:
            pass

    def refresh_explorers(self):
        self.load_desktop_icons()
        # if an explorer window is open, call refresh_view
        for win in self.open_windows.values():
            content = win.content_container.layout().itemAt(0).widget()
            if hasattr(content, "refresh_view"):
                content.refresh_view()

    def set_wallpaper_type(self, wp_type):
        self.wallpaper_type = wp_type
        
        # Check if it's a file
        wp_path = os.path.join(os.path.dirname(__file__), "assets", "wallpapers", wp_type)
        if os.path.exists(wp_path):
            self.wallpaper_pixmap = QPixmap(wp_path)
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = float(self.width())
        h = float(self.height())
        
        if self.wallpaper_type.lower().endswith(('.png', '.jpg', '.jpeg')) and self.wallpaper_pixmap:
            # Draw our beautiful generated wallpaper scaled to fit
            scaled_pixmap = self.wallpaper_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            # Center it
            px = (self.width() - scaled_pixmap.width()) // 2
            py = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(px, py, scaled_pixmap)
        elif self.wallpaper_type == "wallpaper" and self.wallpaper_pixmap:
            # Fallback legacy check
            scaled_pixmap = self.wallpaper_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            px = (self.width() - scaled_pixmap.width()) // 2
            py = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(px, py, scaled_pixmap)
        else:
            # Draw fallback gradients/colors
            color_map = {
                "dark": (QColor("#1a1e29"), QColor("#0d1017")),
                "pink": (QColor("#f8a5c2"), QColor("#f78fb3")),
                "green": (QColor("#2ecc71"), QColor("#27ae60")),
                "orange": (QColor("#e67e22"), QColor("#d35400")),
                "wallpaper": (QColor("#3eaefc"), QColor("#005fa3")) # fallback sky blue
            }
            
            c1, c2 = color_map.get(self.wallpaper_type, color_map["wallpaper"])
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)
            
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, self.width(), self.height())
            
            # Draw central transparent glowing pigeon logo outline for aesthetics!
            painter.setBrush(QBrush(QColor("rgba(255, 255, 255, 0.08)")))
            painter.drawEllipse(QPointF(w/2, h/2), h*0.35, h*0.35)
            
            # Stylized wing outline
            path = theme.QPainterPath()
            cx = w/2 - 40
            cy = h/2 - 40
            path.moveTo(cx, cy + 40)
            path.cubicTo(cx + 20, cy, cx + 60, cy + 10, cx + 80, cy + 40)
            path.cubicTo(cx + 60, cy + 60, cx + 30, cy + 60, cx, cy + 40)
            painter.drawPath(path)

    # App Open Orchestration
    def open_app(self, app_id, argument=None):
        # 1. Check if already open
        if app_id in self.open_windows:
            win = self.open_windows[app_id]
            if not win.isVisible():
                taskbar_y = self.main_window.taskbar.y() if self.main_window and self.main_window.taskbar else self.height()
                animations.restore_from_taskbar(win, win.geometry(), taskbar_y, duration=280)
                win.set_active(True)
                win.raise_()
                self.focus_changed(app_id)
            else:
                if not argument:
                    # User clicked taskbar for active window -> Minimize it
                    win.minimize_window()
                else:
                    win.show()
                    win.set_active(True)
                    win.raise_()
                    self.focus_changed(app_id)
            
            # If argument (file) passed, load it
            if argument and app_id == "notepad":
                win.content_container.layout().itemAt(0).widget().load_file(argument)
            return win
            
        # 2. Instantiate App Widgets
        title = "App"
        icon_name = "logo"
        content_widget = None
        width, height = 580, 400
        
        if app_id == "explorer":
            title = "Files"
            icon_name = "folder"
            content_widget = SigeonExplorer(self)
            content_widget.open_file_requested.connect(self.open_file)
            width, height = 700, 480
            
        elif app_id == "settings":
            title = "Settings"
            icon_name = "settings"
            content_widget = SigeonSettings(self)
            width, height = 700, 480
            
        elif app_id == "terminal":
            title = "Terminal"
            icon_name = "terminal"
            content_widget = SigeonTerminal(self)
            width, height = 550, 360
            
        elif app_id == "tty":
            title = "Host TTY"
            icon_name = "terminal"
            content_widget = SigeonTTY(self)
            width, height = 650, 420
            
        elif app_id == "notepad":
            title = "Feather Notes"
            icon_name = "notepad"
            content_widget = SigeonNotepad(file_obj=argument, desktop_parent=self)
            width, height = 520, 380
            
        elif app_id == "paint":
            title = "Pigeon Paint"
            icon_name = "photos"
            content_widget = SigeonPaint(self)
            width, height = 660, 480
            
        elif app_id == "weather":
            title = "Pigeon Weather"
            icon_name = "weather"
            content_widget = SigeonWeather(self)
            width, height = 480, 360
            
        elif app_id == "photos":
            title = "Photos"
            icon_name = "photos"
            content_widget = SigeonPhotos(self)
            width, height = 520, 360
            
        elif app_id == "flappy_game":
            title = "Flappy Pigeon"
            icon_name = "logo"
            content_widget = FlappyPigeonGame(self)
            width, height = 400, 340
            
        elif app_id == "about":
            # Shows settings app with row activated to the last spec page
            win = self.open_app("settings")
            # Navigate to last item "About Sigeon OS" (Index 10)
            win.content_container.layout().itemAt(0).widget().menu_list.setCurrentRow(10)
            return win
            
        elif app_id == "recycle":
            QMessageBox.information(self, "Recycle Bin", "Recycle Bin is currently empty. Coo!")
            return None
            
        else:
            return None
            
        # 3. Create movable window wrapper
        win = SigeonWindow(app_id, title, icon_name, self, content_widget)
        win.resize(width, height)
        
        # Stagger position
        margin_x = 100 + self.stagger_count * 25
        margin_y = 60 + self.stagger_count * 25
        win.move(margin_x, margin_y)
        self.stagger_count = (self.stagger_count + 1) % 6
        
        # Connect Signals
        win.closed.connect(self.window_closed)
        win.minimized.connect(self.window_minimized)
        win.activated.connect(self.focus_changed)
        
        animations.pop_in(win, duration=300)
        win.set_active(True)
        win.raise_()
        
        # Keep references
        self.open_windows[app_id] = win
        self.focus_changed(app_id)
        
        return win

    # File Association Handler (e.g. double clicking a file in File Explorer)
    def open_file(self, filename, file_obj):
        if not file_obj or not isinstance(file_obj, VirtualFile):
            return
            
        ext = file_obj.file_type.lower()
        if ext == "txt":
            self.open_app("notepad", file_obj)
        elif ext in ("png", "jpg"):
            win = self.open_app("photos")
            # Set selected index in photos list to match png
            photos_widget = win.content_container.layout().itemAt(0).widget()
            if filename == "Screenshot_2024-05-20.png":
                photos_widget.photo_list.setCurrentRow(0)
            elif filename == "Coop Nest Sketch.png":
                photos_widget.photo_list.setCurrentRow(1)
            elif filename == "Scatter Crumbs.png":
                photos_widget.photo_list.setCurrentRow(2)
        elif ext == "pdf":
            QMessageBox.information(self, "PDF Reader", f"Opening PDF: {filename}\n\nContent:\n{file_obj.content}")
        elif ext == "mp3":
            QMessageBox.information(self, "Audio Player", f"Playing Track: {filename}\n\nContent:\n{file_obj.content}")
        elif ext == "sgpj":
            QMessageBox.information(self, "Flight Plan Editor", f"Opening Flight Plan:\n\n{file_obj.content}")
        else:
            QMessageBox.information(self, "Sigeon File Manager", f"Opening file: {filename}\n\nDescription:\n{file_obj.content}")

    # Window Manager Events
    def window_closed(self, app_id):
        if app_id in self.open_windows:
            del self.open_windows[app_id]
        if self.main_window and self.main_window.taskbar:
            self.main_window.taskbar.set_app_active(app_id, False)

    def window_minimized(self, app_id):
        if self.main_window and self.main_window.taskbar:
            self.main_window.taskbar.set_app_active(app_id, False)

    def focus_changed(self, active_app_id):
        # Update focus styling on all windows
        for app_id, win in self.open_windows.items():
            if app_id == active_app_id:
                win.set_active(True)
                if self.main_window and self.main_window.taskbar:
                    self.main_window.taskbar.set_app_active(app_id, True)
            else:
                win.set_active(False)
                if self.main_window and self.main_window.taskbar:
                    # If open but not in focus, it can have standard status
                    pass

    # Helper: Refresh explorer lists when notepad saves
    def refresh_explorers(self):
        for app_id, win in self.open_windows.items():
            if app_id == "explorer":
                explorer_widget = win.content_container.layout().itemAt(0).widget()
                explorer_widget.refresh_view()
