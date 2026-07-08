import os
import random
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QSize, QTimer
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush, QLinearGradient, QRadialGradient, QPen, QMouseEvent
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
from apps.browser import SigeonBrowser
from apps.sigeon_ai import SigeonAIApp
from apps.calendar_app import SigeonCalendarApp
from apps.liquid_glass import SigeonLiquidGlassWidget
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
        self.wallpaper_type = "wallpaper.png" # default to original wallpaper
        self.liquid_glass_enabled = True # active by default!
        
        # Load wallpaper pixmap
        self.wallpaper_pixmap = None
        wp_path = os.path.join(os.path.dirname(__file__), "assets", "wallpaper.png")
        if os.path.exists(wp_path):
            self.wallpaper_pixmap = QPixmap(wp_path)
            
        self.icon_widgets = []
        self.liquid_glass_widget = None
        
        # Liquid Glass Wallpaper State
        self.liquid_blobs = []
        self.wallpaper_timer = QTimer(self)
        self.wallpaper_timer.timeout.connect(self.animate_wallpaper)
        self.init_liquid_blobs()
        
        self._cached_background = None
        self._cached_overlay = None
        self._caches_dirty = True
        
        if self.liquid_glass_enabled:
            self.wallpaper_timer.start(10) # Ultra Performance Mode (~100 FPS)
            
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
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
            ("SigeonAI", "logo_white", "sigeon_ai", False, None),
            ("Browser", "wing_drive", "browser", False, None),
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
            
        # Instantiate and show Liquid Glass floating widget
        if self.liquid_glass_widget is None:
            self.liquid_glass_widget = SigeonLiquidGlassWidget(self)
        self.reposition_glass_widget()
        self.liquid_glass_widget.show()

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
        elif wp_type == "wallpaper.png":
            wp_path = os.path.join(os.path.dirname(__file__), "assets", "wallpaper.png")
            if os.path.exists(wp_path):
                self.wallpaper_pixmap = QPixmap(wp_path)
            
        self._caches_dirty = True
        self.update()

    def set_liquid_glass_enabled(self, enabled):
        self.liquid_glass_enabled = enabled
        self._caches_dirty = True
        if enabled:
            if not self.wallpaper_timer.isActive():
                self.wallpaper_timer.start(10)
        else:
            self.wallpaper_timer.stop()
        self.update()

    def init_liquid_blobs(self):
        colors = [
            (QColor("#FF2A54"), QColor("rgba(255, 42, 84, 0)")),    # Deep Pink/Red
            (QColor("#00F2FE"), QColor("rgba(0, 242, 254, 0)")),    # Cyan
            (QColor("#7000FF"), QColor("rgba(112, 0, 255, 0)")),    # Violet
            (QColor("#FF9A00"), QColor("rgba(255, 154, 0, 0)")),    # Orange
            (QColor("#05DFD7"), QColor("rgba(5, 223, 215, 0)")),    # Teal
            (QColor("#D600FF"), QColor("rgba(214, 0, 255, 0)")),    # Magenta
        ]
        import math
        import random
        self.liquid_blobs = []
        for i, (c_start, c_end) in enumerate(colors):
            radius = random.uniform(600, 900)
            x = random.uniform(-100, 1920 + 100)
            y = random.uniform(-100, 1080 + 100)
            speed = random.uniform(1.0, 2.0)
            angle = random.uniform(0, 2 * math.pi)
            
            self.liquid_blobs.append({
                'x': x,
                'y': y,
                'radius': radius,
                'c_start': c_start,
                'c_end': c_end,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed
            })

    def play_jingle(self):
        from PyQt6.QtMultimedia import QSoundEffect
        from PyQt6.QtCore import QUrl
        import os
        if not hasattr(self, 'jingle_player'):
            self.jingle_player = QSoundEffect()
            sound_path = os.path.join(os.path.dirname(__file__), "assets", "boot.mp3")
            if os.path.exists(sound_path):
                self.jingle_player.setSource(QUrl.fromLocalFile(sound_path))
                self.jingle_player.setVolume(0.8)
        self.jingle_player.play()

    def stir_liquid_glass(self, x, y, dx, dy):
        if not self.liquid_glass_enabled:
            return
            
        speed = (dx**2 + dy**2)**0.5
        if speed < 2:
            return
            
        import time, random
        # Play Jingle sound if shaken really hard!
        if speed > 40:
            now = time.time()
            if not hasattr(self, "last_jingle_time"):
                self.last_jingle_time = 0
            if now - self.last_jingle_time > 0.4:
                self.last_jingle_time = now
                self.play_jingle()

        # Massively accelerate liquid blobs
        for b in self.liquid_blobs:
            dist = max(1, ((b['x'] - x)**2 + (b['y'] - y)**2)**0.5)
            force = (8000 / dist) * (speed / 10.0)
            if force > 60: force = 60
            
            b['dx'] += (dx / speed) * force
            b['dy'] += (dy / speed) * force
            
            # Friction / Max speed clamp
            bspeed = (b['dx']**2 + b['dy']**2)**0.5
            if bspeed > 45:
                b['dx'] = (b['dx']/bspeed) * 45
                b['dy'] = (b['dy']/bspeed) * 45

        # Create Splash Ripples
        if not hasattr(self, 'ripples'):
            self.ripples = []
            
        if random.random() < 0.5 and speed > 10:
            self.ripples.append({
                'x': x + random.randint(-40, 40),
                'y': y + random.randint(-40, 40),
                'radius': 10.0,
                'max_radius': random.uniform(150, 500),
                'alpha': 255.0,
                'color': random.choice([b['c_start'] for b in self.liquid_blobs])
            })

    def animate_wallpaper(self):
        if not self.liquid_glass_enabled:
            self.wallpaper_timer.stop()
            return
            
        w = self.width() if self.width() > 0 else 1920
        h = self.height() if self.height() > 0 else 1080
        
        # We bounce the centers, not the edges, since blobs are huge ambient lights
        padding = 300 
        for b in self.liquid_blobs:
            b['x'] += b['dx']
            b['y'] += b['dy']
            
            if b['x'] < -padding:
                b['x'] = -padding
                b['dx'] = abs(b['dx'])
            elif b['x'] > w + padding:
                b['x'] = w + padding
                b['dx'] = -abs(b['dx'])
                
            if b['y'] < -padding:
                b['y'] = -padding
                b['dy'] = abs(b['dy'])
            elif b['y'] > h + padding:
                b['y'] = h + padding
                b['dy'] = -abs(b['dy'])
                
        # Animate ripples
        if hasattr(self, 'ripples'):
            for r in self.ripples[:]:
                r['radius'] += 18.0 # fast expansion
                r['alpha'] -= 7.0 # fade out
                if r['alpha'] <= 0 or r['radius'] >= r['max_radius']:
                    self.ripples.remove(r)
                    
        # Add friction to blobs so they slow down after stirring
        for b in self.liquid_blobs:
            b['dx'] *= 0.98
            b['dy'] *= 0.98
            
            # ensure minimum speed so they don't stop entirely
            bspeed = (b['dx']**2 + b['dy']**2)**0.5
            if bspeed < 1.2 and bspeed > 0:
                b['dx'] = (b['dx']/bspeed) * 1.2
                b['dy'] = (b['dy']/bspeed) * 1.2

        self.update()

    def reposition_glass_widget(self):
        if self.liquid_glass_widget:
            w = self.width() if self.width() > 0 else 1920
            widget_w = self.liquid_glass_widget.width()
            self.liquid_glass_widget.move(w - widget_w - 40, 40)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reposition_glass_widget()
        self._caches_dirty = True
        if self.liquid_glass_enabled and not self.wallpaper_timer.isActive():
            self.wallpaper_timer.start(10)

    def _build_caches(self, w, h):
        self._cached_background = QPixmap(int(w), int(h))
        self._cached_background.fill(Qt.GlobalColor.transparent)
        p_bg = QPainter(self._cached_background)
        p_bg.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_wallpaper(p_bg, w, h)
        if self.liquid_glass_enabled:
            p_bg.setBrush(QBrush(QColor(10, 15, 25, 190)))
            p_bg.setPen(Qt.PenStyle.NoPen)
            p_bg.drawRect(0, 0, int(w), int(h))
        p_bg.end()
        
        self._cached_overlay = QPixmap(int(w), int(h))
        self._cached_overlay.fill(Qt.GlobalColor.transparent)
        if self.liquid_glass_enabled:
            p_ov = QPainter(self._cached_overlay)
            p_ov.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            p_ov.setBrush(QBrush(QColor(255, 255, 255, 10)))
            p_ov.setPen(Qt.PenStyle.NoPen)
            p_ov.drawRect(0, 0, int(w), int(h))
            
            glass_pen = QPen(QColor(255, 255, 255, 30), 1.5)
            p_ov.setPen(glass_pen)
            p_ov.drawLine(0, 0, int(w), int(h))
            p_ov.drawLine(0, int(h * 0.3), int(w * 0.7), int(h))
            p_ov.drawLine(int(w * 0.3), 0, int(w), int(h * 0.7))
            
            dot_pen = QPen(QColor(255, 255, 255, 20), 1.5)
            p_ov.setPen(dot_pen)
            grid_spacing = 30
            for x in range(0, int(w), grid_spacing):
                for y in range(0, int(h), grid_spacing):
                    p_ov.drawPoint(x, y)
            p_ov.end()

    def _draw_wallpaper(self, painter, w, h):
        if self.wallpaper_type.lower().endswith(('.png', '.jpg', '.jpeg')) and self.wallpaper_pixmap:
            scaled_pixmap = self.wallpaper_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            px = (int(w) - scaled_pixmap.width()) // 2
            py = (int(h) - scaled_pixmap.height()) // 2
            painter.drawPixmap(px, py, scaled_pixmap)
        elif self.wallpaper_type == "wallpaper" and self.wallpaper_pixmap:
            scaled_pixmap = self.wallpaper_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            px = (int(w) - scaled_pixmap.width()) // 2
            py = (int(h) - scaled_pixmap.height()) // 2
            painter.drawPixmap(px, py, scaled_pixmap)
        else:
            color_map = {
                "dark": (QColor("#1a1e29"), QColor("#0d1017")),
                "pink": (QColor("#f8a5c2"), QColor("#f78fb3")),
                "green": (QColor("#2ecc71"), QColor("#27ae60")),
                "orange": (QColor("#e67e22"), QColor("#d35400")),
                "black": (QColor("#000000"), QColor("#050505")),
                "wallpaper": (QColor("#3eaefc"), QColor("#005fa3"))
            }
            
            c1, c2 = color_map.get(self.wallpaper_type, color_map["wallpaper"])
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)
            
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, int(w), int(h))
            
            if self.wallpaper_type != "black":
                painter.setBrush(QBrush(QColor("rgba(255, 255, 255, 0.08)")))
                painter.drawEllipse(QPointF(w/2, h/2), h*0.35, h*0.35)
                
                path = theme.QPainterPath()
                cx = w/2 - 40
                cy = h/2 - 40
                path.moveTo(cx, cy + 40)
                path.cubicTo(cx + 20, cy, cx + 60, cy + 10, cx + 80, cy + 40)
                path.cubicTo(cx + 60, cy + 60, cx + 30, cy + 60, cx, cy + 40)
                painter.drawPath(path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = float(self.width())
        h = float(self.height())
        
        if w <= 0 or h <= 0:
            return
            
        if getattr(self, '_caches_dirty', True) or self._cached_background is None or self._cached_overlay is None or self._cached_background.size() != self.size():
            self._build_caches(w, h)
            self._caches_dirty = False
            
        # 1. Draw base background cache
        painter.drawPixmap(0, 0, self._cached_background)
        
        # 2. Draw Liquid Glass Overlay dynamic elements if enabled
        if self.liquid_glass_enabled:
            # Draw animated vibrant liquid blobs using Screen mode for light-like mixing
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
            for b in self.liquid_blobs:
                grad = QRadialGradient(b['x'], b['y'], b['radius'], b['x'], b['y'])
                grad.setColorAt(0.0, b['c_start'])
                grad.setColorAt(0.3, QColor(b['c_start'].red(), b['c_start'].green(), b['c_start'].blue(), 200))
                grad.setColorAt(1.0, b['c_end'])
                
                painter.setBrush(QBrush(grad))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(b['x'], b['y']), b['radius'], b['radius'])
                
            # Draw splash ripples
            if hasattr(self, 'ripples'):
                for r in self.ripples:
                    grad = QRadialGradient(r['x'], r['y'], r['radius'], r['x'], r['y'])
                    # vibrant ripple center
                    alpha_val = int(max(0, min(255, r['alpha'] * 0.4)))
                    grad.setColorAt(0.0, QColor(r['color'].red(), r['color'].green(), r['color'].blue(), 0))
                    grad.setColorAt(0.7, QColor(r['color'].red(), r['color'].green(), r['color'].blue(), alpha_val))
                    grad.setColorAt(1.0, QColor(r['color'].red(), r['color'].green(), r['color'].blue(), 0))
                    
                    painter.setBrush(QBrush(grad))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(QPointF(r['x'], r['y']), r['radius'], r['radius'])
                
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            
            # 3. Draw Top Frosted Glass shine reflections cache
            painter.drawPixmap(0, 0, self._cached_overlay)

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

        elif app_id == "browser":
            title = "Feather Browser"
            icon_name = "wing_drive"
            content_widget = SigeonBrowser(self)
            width, height = 900, 620

        elif app_id == "sigeon_ai":
            title = "SigeonAI"
            icon_name = "logo_white"
            content_widget = SigeonAIApp(self)
            width, height = 960, 660

        elif app_id == "calendar":
            title = "Calendar"
            icon_name = "settings"
            content_widget = SigeonCalendarApp(self)
            width, height = 680, 420
            
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

    def open_real_file(self, abs_path):
        """Open a real host OS file using the system default app, or in Notepad if text."""
        import subprocess, sys as _sys
        ext = abs_path.rsplit(".", 1)[-1].lower() if "." in abs_path else ""
        if ext in ("txt", "py", "md", "log", "cfg", "ini", "json", "yaml", "yml", "sh", "bat", "xml", "csv"):
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                vfile = VirtualFile(
                    name=abs_path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1],
                    file_type=ext,
                    content=content,
                    location=abs_path,
                    date=""
                )
                self.open_app("notepad", vfile)
                return
            except Exception:
                pass
        try:
            import os as _os
            if _sys.platform == "win32":
                _os.startfile(abs_path)
            elif _sys.platform == "darwin":
                subprocess.Popen(["open", abs_path])
            else:
                subprocess.Popen(["xdg-open", abs_path])
        except Exception:
            pass

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

    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        import time
        key_text = event.text().upper()
        if key_text:
            now = time.time()
            if not hasattr(self, 'last_key_time'):
                self.last_key_time = 0
                self.crash_buffer = ""
            
            # Reset buffer if more than 5 seconds passed
            if now - self.last_key_time > 5.0:
                self.crash_buffer = ""
                
            self.last_key_time = now
            self.crash_buffer += key_text
            self.crash_buffer = self.crash_buffer[-8:]
            
            if self.crash_buffer == "123CRASH":
                self.crash_buffer = ""
                raise RuntimeError("Manual crash triggered by user sequence (1+2+3+C+R+A+S+H)")
        super().keyPressEvent(event)
