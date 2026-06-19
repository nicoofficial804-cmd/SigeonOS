import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QColorDialog, QFileDialog, QLabel, QComboBox, QFrame)
from PyQt6.QtGui import QPainter, QImage, QColor, QPen, QAction
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
import theme

class PaintCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.drawing = False
        self.my_pen_width = 3
        self.my_pen_color = Qt.GlobalColor.black
        self.last_point = QPoint()
        
        # We use a white image as canvas
        self.image = QImage(self.size(), QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)

    def set_pen_color(self, new_color):
        self.my_pen_color = new_color

    def set_pen_width(self, new_width):
        self.my_pen_width = new_width

    def clear_image(self):
        self.image.fill(Qt.GlobalColor.white)
        self.update()

    def save_image(self, filename):
        if self.image.save(filename):
            return True
        return False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_point = event.position().toPoint()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            self.draw_line_to(event.position().toPoint())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.draw_line_to(event.position().toPoint())
            self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        dirty_rect = event.rect()
        painter.drawImage(dirty_rect, self.image, dirty_rect)

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            new_width = max(self.width() + 128, self.image.width())
            new_height = max(self.height() + 128, self.image.height())
            self.resize_image(self.image, QSize(new_width, new_height))
            self.update()
        super().resizeEvent(event)

    def resize_image(self, image, new_size):
        if image.size() == new_size:
            return
        new_image = QImage(new_size, QImage.Format.Format_RGB32)
        new_image.fill(Qt.GlobalColor.white)
        painter = QPainter(new_image)
        painter.drawImage(QPoint(0, 0), image)
        self.image = new_image

    def draw_line_to(self, end_point):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.my_pen_color, self.my_pen_width,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawLine(self.last_point, end_point)
        
        # Ensure we only update the region that changed
        rad = self.my_pen_width / 2 + 2
        
        # Calculate bounding rect of the line drawn
        p1 = self.last_point
        p2 = end_point
        
        x1 = min(p1.x(), p2.x()) - rad
        y1 = min(p1.y(), p2.y()) - rad
        x2 = max(p1.x(), p2.x()) + rad
        y2 = max(p1.y(), p2.y()) + rad
        
        update_rect = QRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))
        
        self.update(update_rect)
        self.last_point = QPoint(end_point)


class SigeonPaint(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Toolbar
        self.toolbar = QFrame(self)
        self.toolbar.setFixedHeight(50)
        self.toolbar.setStyleSheet("background-color: #f3f3f3; border-bottom: 1px solid rgba(0, 0, 0, 0.1);")
        
        self.toolbar_lay = QHBoxLayout(self.toolbar)
        self.toolbar_lay.setContentsMargins(10, 5, 10, 5)
        self.toolbar_lay.setSpacing(8)

        # Color Button
        self.btn_color = QPushButton("Color", self.toolbar)
        self.btn_color.setStyleSheet(self.get_btn_style())
        self.btn_color.clicked.connect(self.choose_color)
        self.toolbar_lay.addWidget(self.btn_color)

        # Brush Size
        self.lbl_size = QLabel("Size:", self.toolbar)
        self.toolbar_lay.addWidget(self.lbl_size)

        self.combo_size = QComboBox(self.toolbar)
        self.combo_size.addItems(["1", "3", "5", "10", "15", "20", "30"])
        self.combo_size.setCurrentText("3")
        self.combo_size.currentTextChanged.connect(self.change_width)
        self.combo_size.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background: white;
            }
        """)
        self.toolbar_lay.addWidget(self.combo_size)

        # Clear Button
        self.btn_clear = QPushButton("Clear", self.toolbar)
        self.btn_clear.setStyleSheet(self.get_btn_style())
        self.btn_clear.clicked.connect(self.clear_canvas)
        self.toolbar_lay.addWidget(self.btn_clear)

        self.toolbar_lay.addStretch()

        # Save Button
        self.btn_save = QPushButton("Save Image", self.toolbar)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f82df;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #3fa5fc;
            }
        """)
        self.btn_save.clicked.connect(self.save_file)
        self.toolbar_lay.addWidget(self.btn_save)

        self.layout.addWidget(self.toolbar)

        # Canvas container
        self.canvas_container = QWidget(self)
        self.canvas_container.setStyleSheet("background-color: #e0e0e0;")
        self.canvas_lay = QVBoxLayout(self.canvas_container)
        self.canvas_lay.setContentsMargins(10, 10, 10, 10)
        
        self.canvas = PaintCanvas(self.canvas_container)
        
        # A shadow could be cool
        import animations
        animations.add_drop_shadow(self.canvas, blur=15, offset_x=2, offset_y=4)
        
        self.canvas_lay.addWidget(self.canvas)
        self.layout.addWidget(self.canvas_container, stretch=1)

    def get_btn_style(self):
        return """
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px 12px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """

    def choose_color(self):
        color = QColorDialog.getColor(self.canvas.my_pen_color, self)
        if color.isValid():
            self.canvas.set_pen_color(color)
            
            # Show the selected color on the button
            self.btn_color.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px 12px;
                    color: {"#ffffff" if color.lightness() < 128 else "#333333"};
                }}
                QPushButton:hover {{
                    border-color: #0f82df;
                }}
            """)

    def change_width(self, text):
        try:
            val = int(text)
            self.canvas.set_pen_width(val)
        except:
            pass

    def clear_canvas(self):
        self.canvas.clear_image()

    def save_file(self):
        # Default save path inside SigeonOS Home
        home_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Home", "Pictures")
        if not os.path.exists(home_path):
            os.makedirs(home_path, exist_ok=True)
            
        initial_path = os.path.join(home_path, "Untitled_Painting.png")
            
        filename, _ = QFileDialog.getSaveFileName(self, "Save Image", initial_path, "PNG Images (*.png);;JPEG Images (*.jpg)")
        if filename:
            self.canvas.save_image(filename)
