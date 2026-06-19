import os
import random
import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QPixmap
import theme
from apps.fs import VirtualFS

class PhotoDrawingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.photo_type = "wallpaper" # wallpaper, nest, crumbs
        self.setMinimumSize(250, 180)

    def set_photo(self, photo_type):
        self.photo_type = photo_type
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = float(self.width())
        h = float(self.height())
        
        # Outer border / frame
        painter.setBrush(QBrush(QColor("#eaeaea")))
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawRect(0, 0, self.width(), self.height())
        
        if os.path.isabs(self.photo_type) and os.path.exists(self.photo_type):
            pixmap = QPixmap(self.photo_type)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                px = (self.width() - scaled.width()) // 2
                py = (self.height() - scaled.height()) // 2
                painter.drawPixmap(px, py, scaled)
        elif self.photo_type == "wallpaper":
            # Draw a mini SigeonOS Wallpaper
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0, QColor("#3eaefc"))
            grad.setColorAt(1, QColor("#005fa3"))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(2, 2, w-4, h-4))
            
            # Sun / Cloud
            painter.setBrush(QBrush(QColor("rgba(255, 255, 255, 0.15)")))
            painter.drawEllipse(QPointF(w/2, h/2), h*0.35, h*0.35)
            painter.drawEllipse(QPointF(w/2, h/2), h*0.25, h*0.25)
            
            # Pigeon wing logo silhouette in white in center
            painter.setBrush(QBrush(QColor("#ffffff")))
            path = theme.QPainterPath()
            cx = w/2 - 20
            cy = h/2 - 20
            path.moveTo(cx, cy + 20)
            path.cubicTo(cx + 10, cy, cx + 30, cy + 5, cx + 40, cy + 20)
            path.cubicTo(cx + 30, cy + 30, cx + 15, cy + 30, cx, cy + 20)
            painter.drawPath(path)
            
        elif self.photo_type == "nest":
            # Draw Coop Nest
            # Sky background
            painter.setBrush(QBrush(QColor("#e0f7fa")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(2, 2, w-4, h-4))
            
            # Wooden Nest box
            painter.setBrush(QBrush(QColor("#a1887f")))
            painter.drawRect(QRectF(w*0.3, h*0.4, w*0.4, h*0.45))
            
            # Roof
            painter.setBrush(QBrush(QColor("#8d6e63")))
            roof = [QPointF(w*0.25, h*0.4), QPointF(w*0.5, h*0.2), QPointF(w*0.75, h*0.4)]
            painter.drawPolygon(roof)
            
            # Nest entrance hole (black)
            painter.setBrush(QBrush(QColor("#3e2723")))
            painter.drawEllipse(QPointF(w*0.5, h*0.58), h*0.14, h*0.14)
            
            # Perch
            painter.setBrush(QBrush(QColor("#d7ccc8")))
            painter.drawRect(QRectF(w*0.45, h*0.72, w*0.1, h*0.04))
            
        elif self.photo_type == "crumbs":
            # Draw Scattered golden breadcrumbs on concrete
            # Concrete background
            painter.setBrush(QBrush(QColor("#b0bec5")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(2, 2, w-4, h-4))
            
            # Stone tile cracks
            painter.setPen(QPen(QColor("#90a4ae"), 1))
            painter.drawLine(QPointF(0.0, h*0.3), QPointF(w, h*0.4))
            painter.drawLine(QPointF(w*0.5, h*0.35), QPointF(w*0.4, h))
            
            # Scattered Crumbs (yellow ellipses)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#ffb300")))
            
            random.seed(192) # Stable layout
            for i in range(12):
                cx = random.uniform(w*0.1, w*0.9)
                cy = random.uniform(h*0.1, h*0.9)
                rx = random.uniform(3, 7)
                ry = random.uniform(2, 4)
                rot = random.uniform(0, 180)
                
                painter.save()
                painter.translate(cx, cy)
                painter.rotate(rot)
                painter.drawEllipse(QRectF(-rx, -ry, rx*2, ry*2))
                painter.restore()

class SigeonPhotos(QWidget):
    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Sidebar for photos list
        self.sidebar = QWidget(self)
        self.sidebar.setObjectName("explorer_sidebar")
        self.sidebar.setFixedWidth(150)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 10, 0, 10)
        
        self.lbl_title = QLabel(" Photos Gallery", self.sidebar)
        self.lbl_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        self.sidebar_layout.addWidget(self.lbl_title)
        
        self.photo_list = QListWidget(self.sidebar)
        self.photo_list.setObjectName("explorer_sidebar_list")
        self.photo_list.currentRowChanged.connect(self.photo_selected)
        self.sidebar_layout.addWidget(self.photo_list)
        
        self.layout.addWidget(self.sidebar)
        
        # Main Viewer Panel
        self.viewer_panel = QWidget(self)
        self.viewer_panel.setStyleSheet("background-color: #ffffff;")
        self.viewer_layout = QVBoxLayout(self.viewer_panel)
        self.viewer_layout.setContentsMargins(12, 12, 12, 12)
        
        top_lay = QHBoxLayout()
        self.photo_title = QLabel("Wallpaper Preview.png", self.viewer_panel)
        self.photo_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1a1f26;")
        top_lay.addWidget(self.photo_title)
        
        self.btn_set_wp = QPushButton("Set as Wallpaper", self.viewer_panel)
        self.btn_set_wp.setStyleSheet("background-color: #0f82df; color: white; padding: 4px 8px; border-radius: 4px;")
        self.btn_set_wp.clicked.connect(self.set_wallpaper)
        top_lay.addWidget(self.btn_set_wp, 0, Qt.AlignmentFlag.AlignRight)
        
        self.viewer_layout.addLayout(top_lay)
        
        self.canvas = PhotoDrawingWidget(self.viewer_panel)
        self.viewer_layout.addWidget(self.canvas, stretch=1)
        
        self.layout.addWidget(self.viewer_panel)
        
        # Populating list
        self.photos_data = [
            ("Wallpaper Preview.png", "wallpaper"),
            ("Coop Nest Sketch.png", "nest"),
            ("Scatter Crumbs.png", "crumbs")
        ]
        
        fs = VirtualFS()
        pics_node = fs.get_node(["Home", "Pictures"])
        if isinstance(pics_node, dict):
            for fname, fobj in pics_node.items():
                if not isinstance(fobj, dict) and fobj.file_type in ("png", "jpg", "jpeg", "bmp"):
                    self.photos_data.append((fname, fobj.content)) # absolute path

        for name, val in self.photos_data:
            item = QListWidgetItem(name)
            item.setIcon(theme.IconFactory.get_icon("photos", 16))
            self.photo_list.addItem(item)
            
        self.photo_list.setCurrentRow(0)

    def set_wallpaper(self):
        idx = self.photo_list.currentRow()
        if 0 <= idx < len(self.photos_data):
            name, p_type = self.photos_data[idx]
            if os.path.isabs(p_type) and self.desktop:
                # Assuming desktop.py change_wallpaper can handle absolute path
                # Let's set it by absolute path! Wait, set_wallpaper_type appends "assets/wallpapers/" if not absolute.
                # Oh, earlier in desktop.py I did: `os.path.join(..., wp_type)`. If wp_type is absolute, os.path.join ignores the base path in Python!
                self.desktop.set_wallpaper_type(p_type)

    def photo_selected(self, index):
        if 0 <= index < len(self.photos_data):
            name, p_type = self.photos_data[index]
            self.photo_title.setText(name)
            self.canvas.set_photo(p_type)
