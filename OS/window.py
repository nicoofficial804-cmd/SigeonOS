from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizeGrip
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QMouseEvent
import theme
import animations

class SigeonWindow(QFrame):
    # Signals for window manager
    closed = pyqtSignal(str)      # Emits app_id when closed
    minimized = pyqtSignal(str)   # Emits app_id when minimized
    activated = pyqtSignal(str)   # Emits app_id when clicked / gains focus

    def __init__(self, app_id, title, icon_name, parent_desktop, content_widget):
        super().__init__(parent_desktop)
        self.app_id = app_id
        self.title = title
        self.icon_name = icon_name
        self.desktop = parent_desktop
        
        # Window State
        self.is_maximized = False
        self.normal_geometry = None
        self.drag_position = QPoint()
        
        # Setup UI
        self.init_ui(content_widget)
        
        # Dragging variables
        self._is_dragging = False

    def init_ui(self, content_widget):
        # Set styling properties
        self.setObjectName("sigeon_window_frame")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setWindowFlags(Qt.WindowType.SubWindow)
        
        # Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Custom Titlebar
        self.titlebar = QWidget(self)
        self.titlebar.setObjectName("titlebar_widget")
        self.titlebar.setFixedHeight(34)
        
        self.titlebar_layout = QHBoxLayout(self.titlebar)
        self.titlebar_layout.setContentsMargins(10, 0, 10, 0)
        self.titlebar_layout.setSpacing(8)
        
        # Icon
        self.icon_label = QLabel(self.titlebar)
        self.icon_label.setPixmap(theme.IconFactory.get_icon(self.icon_name, 18).pixmap(18, 18))
        self.titlebar_layout.addWidget(self.icon_label)
        
        # Title Text
        self.title_label = QLabel(self.title, self.titlebar)
        self.title_label.setObjectName("title_label")
        self.titlebar_layout.addWidget(self.title_label)
        self.titlebar_layout.addStretch()
        
        # Minimize Button
        self.btn_min = QPushButton(self.titlebar)
        self.btn_min.setObjectName("win_btn_min")
        self.btn_min.setFixedSize(28, 28)
        self.btn_min.setIcon(theme.IconFactory.get_icon("logo_white", 12)) # simple dot icon or similar
        # We can draw standard line with painter, or just text
        self.btn_min.setText("—")
        self.btn_min.setStyleSheet("color: #333333; font-weight: bold; font-size: 10px;")
        self.btn_min.clicked.connect(self.minimize_window)
        self.titlebar_layout.addWidget(self.btn_min)
        
        # Maximize Button
        self.btn_max = QPushButton(self.titlebar)
        self.btn_max.setObjectName("win_btn_max")
        self.btn_max.setFixedSize(28, 28)
        self.btn_max.setText("❑")
        self.btn_max.setStyleSheet("color: #333333; font-size: 10px;")
        self.btn_max.clicked.connect(self.toggle_maximize)
        self.titlebar_layout.addWidget(self.btn_max)
        
        # Close Button
        self.btn_close = QPushButton(self.titlebar)
        self.btn_close.setObjectName("win_btn_close")
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.setText("✕")
        self.btn_close.setStyleSheet("QPushButton#win_btn_close { color: #333333; font-size: 11px; } QPushButton#win_btn_close:hover { color: white; }")
        self.btn_close.clicked.connect(self.close_window)
        self.titlebar_layout.addWidget(self.btn_close)
        
        self.main_layout.addWidget(self.titlebar)
        
        # 2. Separator line
        self.sep = QFrame()
        self.sep.setFrameShape(QFrame.Shape.HLine)
        self.sep.setFrameShadow(QFrame.Shadow.Sunken)
        self.sep.setStyleSheet("background-color: rgba(0,0,0,0.06); border: none; height: 1px;")
        self.main_layout.addWidget(self.sep)
        
        # 3. Content Widget Container
        self.content_container = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(content_widget)
        self.main_layout.addWidget(self.content_container)
        
        # 4. Size Grip (for resizing)
        self.sizegrip = QSizeGrip(self)
        self.sizegrip.setFixedSize(14, 14)
        # Position sizegrip at bottom right
        self.main_layout.addWidget(self.sizegrip, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        
        # Install event filter on titlebar for dragging
        self.titlebar.mousePressEvent = self.titlebar_press
        self.titlebar.mouseMoveEvent = self.titlebar_move
        self.titlebar.mouseReleaseEvent = self.titlebar_release
        self.titlebar.mouseDoubleClickEvent = self.titlebar_double_click
        
        # Apply standard styles
        self.setStyleSheet(theme.get_stylesheet())
        
        # Size limit
        self.setMinimumSize(300, 200)

    # Focus/Activation handling
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        self.set_active(True)
        self.activated.emit(self.app_id)
        self.raise_()

    def set_active(self, active):
        if active:
            self.setObjectName("sigeon_window_frame")
            self.title_label.setStyleSheet("color: #1a1f26; font-weight: 500;")
        else:
            self.setObjectName("sigeon_window_frame_inactive")
            self.title_label.setStyleSheet("color: #606f7b; font-weight: normal;")
        self.style().polish(self)

    # Window Actions
    def close_window(self):
        def finish_close():
            self.closed.emit(self.app_id)
            self.deleteLater()
        animations.pop_out(self, duration=200, callback=finish_close)

    def minimize_window(self):
        taskbar_y = self.desktop.height() - 48
        if self.desktop.main_window and self.desktop.main_window.taskbar:
            taskbar_y = self.desktop.main_window.taskbar.y()
            
        def finish_min():
            self.minimized.emit(self.app_id)
            
        animations.minimize_to_taskbar(self, taskbar_y, duration=220, callback=finish_min)

    def toggle_maximize(self):
        if self.is_maximized:
            # Restore normal size
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_maximized = False
            self.sizegrip.show()
        else:
            # Maximize
            self.normal_geometry = self.geometry()
            # Get desktop workspace area minus taskbar
            workspace_height = self.desktop.height() - 48 # taskbar is 48px
            self.setGeometry(0, 0, self.desktop.width(), workspace_height)
            self.is_maximized = True
            self.sizegrip.hide()

    # Dragging Titlebar Events
    def titlebar_press(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and not self.is_maximized:
            self._is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            self.mousePressEvent(event) # Trigger focus on click
            animations.fade_in(self, duration=150, start=1.0, end=0.75)

    def titlebar_move(self, event: QMouseEvent):
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            # Restrict window from going fully offscreen
            new_pos.setY(max(0, new_pos.y())) # don't drag above screen
            
            old_pos = self.pos()
            self.move(new_pos)
            
            dx = new_pos.x() - old_pos.x()
            dy = new_pos.y() - old_pos.y()
            
            self.last_dx = dx
            self.last_dy = dy
            
            if hasattr(self.desktop, 'stir_liquid_glass'):
                self.desktop.stir_liquid_glass(new_pos.x() + self.width()/2, new_pos.y() + self.titlebar.height()/2, dx, dy)
                
            event.accept()

    def titlebar_release(self, event: QMouseEvent):
        if self._is_dragging:
            self._is_dragging = False
            
            # Wobbly Jiggle effect on release if dragged fast
            speed = 0
            if hasattr(self, 'last_dx') and hasattr(self, 'last_dy'):
                speed = (self.last_dx**2 + self.last_dy**2)**0.5
                
            if speed > 15:
                from PyQt6.QtCore import QPropertyAnimation, QPoint, QEasingCurve
                self.jiggle_anim = QPropertyAnimation(self, b"pos")
                self.jiggle_anim.setDuration(600) # bouncy
                
                end_pos = self.pos()
                # Pull the window slightly in the direction of velocity to create an elastic snap back
                pull_pos = end_pos + QPoint(int(self.last_dx), int(self.last_dy))
                
                self.jiggle_anim.setStartValue(pull_pos)
                self.jiggle_anim.setEndValue(end_pos)
                self.jiggle_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
                self.jiggle_anim.start()
                
            animations.fade_in(self, duration=150, start=0.75, end=1.0)

    def titlebar_double_click(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()
            event.accept()
            
    # Resize override to adjust sizegrip position
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position sizegrip at bottom right manually if needed, 
        # though QVBoxLayout with AlignRight/AlignBottom handles it.
        self.sizegrip.move(self.width() - self.sizegrip.width(), self.height() - self.sizegrip.height())
