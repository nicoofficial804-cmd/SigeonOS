import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QPainterPath, QLinearGradient
from PyQt6.QtCore import Qt, QPointF, QRectF

# Theme Colors
ACCENT_BLUE = "#0f82df"      # Standard Sigeon blue
ACCENT_LIGHT = "#3fa5fc"     # Hover/highlight blue
BG_LIGHT_ALPHA = "rgba(245, 247, 250, 0.85)"  # Acrylic light window background
BG_DARK_ALPHA = "rgba(20, 24, 33, 0.85)"      # Acrylic dark taskbar background
BORDER_LIGHT = "rgba(255, 255, 255, 0.4)"
TEXT_DARK = "#1a1f26"
TEXT_LIGHT = "#ffffff"
TEXT_MUTED = "#606f7b"

class IconFactory:
    _cache = {}

    @classmethod
    def get_icon(cls, name, size=64):
        key = f"{name}_{size}"
        if key in cls._cache:
            return cls._cache[key]
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw the specific icon
        if name == "logo":
            cls._draw_logo(painter, size)
        elif name == "logo_white":
            cls._draw_logo_white(painter, size)
        elif name == "wing_white":
            cls._draw_wing_white(painter, size)
        elif name == "folder":
            cls._draw_folder(painter, size, QColor("#3eaefc"), QColor("#0078d4"))
        elif name == "folder_music":
            cls._draw_folder_special(painter, size, "music")
        elif name == "folder_videos":
            cls._draw_folder_special(painter, size, "video")
        elif name == "folder_pictures":
            cls._draw_folder_special(painter, size, "picture")
        elif name == "folder_downloads":
            cls._draw_folder_special(painter, size, "download")
        elif name == "folder_desktop":
            cls._draw_folder_special(painter, size, "desktop")
        elif name == "folder_documents":
            cls._draw_folder_special(painter, size, "document")
        elif name == "folder_projects":
            cls._draw_folder_special(painter, size, "project")
        elif name == "store" or name == "wingstore":
            cls._draw_store(painter, size)
        elif name == "mail":
            cls._draw_mail(painter, size)
        elif name == "calendar":
            cls._draw_calendar(painter, size)
        elif name == "photos":
            cls._draw_photos(painter, size)
        elif name == "settings":
            cls._draw_settings(painter, size)
        elif name == "weather":
            cls._draw_weather(painter, size)
        elif name == "terminal":
            cls._draw_terminal(painter, size)
        elif name == "notepad" or name == "feather_notes":
            cls._draw_notepad(painter, size)
        elif name == "help":
            cls._draw_help(painter, size)
        elif name == "recycle_empty":
            cls._draw_recycle(painter, size, empty=True)
        elif name == "recycle_full":
            cls._draw_recycle(painter, size, empty=False)
        elif name == "pigeon_drive":
            cls._draw_drive(painter, size, label="P")
        elif name == "wing_drive":
            cls._draw_drive(painter, size, label="W")
        elif name == "cloud_nest":
            cls._draw_cloud(painter, size)
        elif name == "file_txt":
            cls._draw_file(painter, size, "TXT", QColor("#e2a812"))
        elif name == "file_pdf":
            cls._draw_file(painter, size, "PDF", QColor("#e01b24"))
        elif name == "file_png":
            cls._draw_file(painter, size, "PNG", QColor("#2ec27e"))
        elif name == "file_mp3":
            cls._draw_file(painter, size, "MP3", QColor("#9b51e0"))
        elif name == "file_generic":
            cls._draw_file(painter, size, "", QColor("#6c7a89"))
        else:
            # Fallback
            cls._draw_logo(painter, size)
            
        painter.end()
        icon = QIcon(pixmap)
        cls._cache[key] = icon
        return icon

    @staticmethod
    def _draw_pigeon_shape(painter, x, y, scale, color):
        # Draw a stylized pigeon
        painter.save()
        painter.translate(x, y)
        painter.scale(scale, scale)
        
        path = QPainterPath()
        # Head & body path
        path.moveTo(10, 32)
        # Tail
        path.lineTo(2, 32)
        path.lineTo(6, 25)
        # Back
        path.quadTo(15, 18, 22, 18)
        # Neck to head
        path.lineTo(24, 12)
        path.arcTo(20, 4, 12, 12, -45, 180)
        # Beak
        path.lineTo(34, 11)
        path.lineTo(31, 14)
        # Breast
        path.quadTo(24, 20, 25, 28)
        path.quadTo(20, 34, 10, 32)
        
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Eye
        painter.setBrush(QBrush(QColor("#0078d4") if color == Qt.GlobalColor.white else Qt.GlobalColor.white))
        painter.drawEllipse(QRectF(27, 8, 2, 2))
        
        # Wing overlay
        wing = QPainterPath()
        wing.moveTo(14, 21)
        wing.quadTo(21, 21, 23, 26)
        wing.quadTo(18, 31, 11, 26)
        wing.lineTo(14, 21)
        painter.setBrush(QBrush(QColor("#eef4fc") if color == Qt.GlobalColor.white else QColor("#5cb3ff")))
        painter.drawPath(wing)
        
        painter.restore()

    @classmethod
    def _draw_logo(cls, painter, size):
        # Blue circle background with white pigeon
        margin = size * 0.05
        rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
        
        grad = QLinearGradient(0, 0, 0, size)
        grad.setColorAt(0, QColor("#3ba6fc"))
        grad.setColorAt(1, QColor("#0060c0"))
        
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)
        
        # Draw white pigeon in the center
        p_scale = size / 55.0
        cls._draw_pigeon_shape(painter, size * 0.18, size * 0.18, p_scale, Qt.GlobalColor.white)

    @classmethod
    def _draw_logo_white(cls, painter, size):
        # Translucent white background with blue pigeon
        margin = size * 0.05
        rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
        painter.setBrush(QBrush(QColor("rgba(255, 255, 255, 0.2)")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)
        
        p_scale = size / 55.0
        cls._draw_pigeon_shape(painter, size * 0.18, size * 0.18, p_scale, QColor("#0078d4"))

    @classmethod
    def _draw_wing_white(cls, painter, size):
        # Draw a single clean wing path in white
        painter.save()
        path = QPainterPath()
        path.moveTo(size * 0.1, size * 0.5)
        path.cubicTo(size * 0.3, size * 0.2, size * 0.7, size * 0.3, size * 0.9, size * 0.5)
        path.cubicTo(size * 0.7, size * 0.7, size * 0.4, size * 0.7, size * 0.1, size * 0.5)
        
        # Feather cuts
        path.moveTo(size * 0.3, size * 0.6)
        path.quadTo(size * 0.5, size * 0.55, size * 0.7, size * 0.6)
        
        painter.setPen(QPen(Qt.GlobalColor.white, size * 0.08, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        painter.restore()

    @classmethod
    def _draw_folder(cls, painter, size, color_top, color_bottom):
        # Draw a beautiful modern Windows 11 style folder
        w = size * 0.8
        h = size * 0.65
        x = (size - w) / 2
        y = (size - h) / 2 + size * 0.05
        
        # Folder Back
        back_path = QPainterPath()
        back_path.moveTo(x, y + h)
        back_path.lineTo(x, y + h * 0.1)
        back_path.quadTo(x, y, x + w * 0.08, y)
        # Tab
        back_path.lineTo(x + w * 0.3, y)
        back_path.lineTo(x + w * 0.38, y + h * 0.1)
        back_path.lineTo(x + w * 0.92, y + h * 0.1)
        back_path.quadTo(x + w, y + h * 0.1, x + w, y + h * 0.2)
        back_path.lineTo(x + w, y + h)
        back_path.closeSubpath()
        
        painter.setPen(Qt.PenStyle.NoPen)
        grad_back = QLinearGradient(0, y, 0, y + h)
        grad_back.setColorAt(0, color_top.lighter(110))
        grad_back.setColorAt(1, color_bottom.darker(110))
        painter.setBrush(QBrush(grad_back))
        painter.drawPath(back_path)
        
        # Folder Front (slightly lower and overlapping)
        front_path = QPainterPath()
        fy = y + h * 0.2
        fh = h * 0.8
        front_path.moveTo(x, y + h)
        front_path.lineTo(x, fy)
        front_path.quadTo(x, fy - h * 0.05, x + w * 0.08, fy - h * 0.05)
        front_path.lineTo(x + w * 0.92, fy - h * 0.05)
        front_path.quadTo(x + w, fy - h * 0.05, x + w, fy)
        front_path.lineTo(x + w, y + h)
        front_path.closeSubpath()
        
        grad_front = QLinearGradient(0, fy, 0, y + h)
        grad_front.setColorAt(0, color_top)
        grad_front.setColorAt(1, color_bottom)
        
        painter.setBrush(QBrush(grad_front))
        painter.drawPath(front_path)

    @classmethod
    def _draw_folder_special(cls, painter, size, type_name):
        # Draw standard folder
        cls._draw_folder(painter, size, QColor("#53bbfc"), QColor("#0073cc"))
        
        # Draw overlay icon in the center of the front flap
        painter.save()
        # center is at size/2, y is slightly offset
        cx = size * 0.5
        cy = size * 0.65
        r = size * 0.15
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("rgba(255, 255, 255, 0.85)")))
        painter.drawEllipse(QPointF(cx, cy), r, r)
        
        painter.setPen(QPen(QColor("#005fa3"), size * 0.03))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        if type_name == "music":
            # Note symbol
            path = QPainterPath()
            path.moveTo(cx - r*0.3, cy + r*0.3)
            path.lineTo(cx - r*0.3, cy - r*0.4)
            path.lineTo(cx + r*0.3, cy - r*0.6)
            path.lineTo(cx + r*0.3, cy + r*0.1)
            painter.drawPath(path)
            painter.setBrush(QBrush(QColor("#005fa3")))
            painter.drawEllipse(QPointF(cx - r*0.4, cy + r*0.3), r*0.2, r*0.15)
            painter.drawEllipse(QPointF(cx + r*0.2, cy + r*0.1), r*0.2, r*0.15)
        elif type_name == "video":
            # Film/Play symbol
            path = QPainterPath()
            path.moveTo(cx - r*0.25, cy - r*0.35)
            path.lineTo(cx + r*0.35, cy)
            path.lineTo(cx - r*0.25, cy + r*0.35)
            path.closeSubpath()
            painter.setBrush(QBrush(QColor("#005fa3")))
            painter.drawPath(path)
        elif type_name == "picture":
            # Image mountain/sun
            painter.setBrush(QBrush(QColor("#005fa3")))
            painter.drawEllipse(QPointF(cx + r*0.2, cy - r*0.2), r*0.12, r*0.12)
            path = QPainterPath()
            path.moveTo(cx - r*0.4, cy + r*0.35)
            path.lineTo(cx - r*0.1, cy - r*0.1)
            path.lineTo(cx + r*0.1, cy + r*0.1)
            path.lineTo(cx + r*0.3, cy - r*0.0)
            path.lineTo(cx + r*0.45, cy + r*0.35)
            path.closeSubpath()
            painter.drawPath(path)
        elif type_name == "download":
            # Down arrow
            path = QPainterPath()
            path.moveTo(cx, cy - r*0.5)
            path.lineTo(cx, cy + r*0.2)
            path.moveTo(cx - r*0.3, cy - r*0.1)
            path.lineTo(cx, cy + r*0.2)
            path.lineTo(cx + r*0.3, cy - r*0.1)
            painter.drawPath(path)
        elif type_name == "desktop":
            # Monitor
            rect = QRectF(cx - r*0.5, cy - r*0.4, r*1.0, r*0.6)
            painter.drawRoundedRect(rect, r*0.1, r*0.1)
            painter.drawLine(QPointF(cx - r*0.2, cy + r*0.35), QPointF(cx + r*0.2, cy + r*0.35))
            painter.drawLine(QPointF(cx, cy + r*0.2), QPointF(cx, cy + r*0.35))
        elif type_name == "document":
            # Text lines
            painter.drawLine(QPointF(cx - r*0.4, cy - r*0.35), QPointF(cx + r*0.4, cy - r*0.35))
            painter.drawLine(QPointF(cx - r*0.4, cy - r*0.1), QPointF(cx + r*0.2, cy - r*0.1))
            painter.drawLine(QPointF(cx - r*0.4, cy + r*0.15), QPointF(cx + r*0.3, cy + r*0.15))
        elif type_name == "project":
            # Brackets or gear
            painter.drawLine(QPointF(cx - r*0.3, cy - r*0.3), QPointF(cx - r*0.5, cy - r*0.3))
            painter.drawLine(QPointF(cx - r*0.5, cy - r*0.3), QPointF(cx - r*0.5, cy + r*0.3))
            painter.drawLine(QPointF(cx - r*0.5, cy + r*0.3), QPointF(cx - r*0.3, cy + r*0.3))
            painter.drawLine(QPointF(cx + r*0.3, cy - r*0.3), QPointF(cx + r*0.5, cy - r*0.3))
            painter.drawLine(QPointF(cx + r*0.5, cy - r*0.3), QPointF(cx + r*0.5, cy + r*0.3))
            painter.drawLine(QPointF(cx + r*0.5, cy + r*0.3), QPointF(cx + r*0.3, cy + r*0.3))
            painter.drawText(QRectF(cx - r*0.4, cy - r*0.4, r*0.8, r*0.8), Qt.AlignmentFlag.AlignCenter, "</>")
            
        painter.restore()

    @classmethod
    def _draw_store(cls, painter, size):
        # WingStore shopping bag
        w = size * 0.7
        h = size * 0.65
        x = (size - w) / 2
        y = size * 0.25
        
        # Bag handle
        painter.setPen(QPen(QColor("#0078d4"), size * 0.05, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(QRectF(size * 0.3, size * 0.1, size * 0.4, size * 0.3), 0, 180 * 16)
        
        # Bag body
        painter.setPen(Qt.PenStyle.NoPen)
        grad = QLinearGradient(0, y, 0, y + h)
        grad.setColorAt(0, QColor("#eef5fc"))
        grad.setColorAt(1, QColor("#bcd6f7"))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(QRectF(x, y, w, h), size * 0.05, size * 0.05)
        
        # Accent wing on bag
        cls._draw_pigeon_shape(painter, size * 0.25, size * 0.35, size / 100.0, QColor("#0f82df"))

    @classmethod
    def _draw_mail(cls, painter, size):
        # Blue envelope
        w = size * 0.8
        h = size * 0.55
        x = (size - w) / 2
        y = (size - h) / 2
        
        grad = QLinearGradient(0, y, 0, y + h)
        grad.setColorAt(0, QColor("#3eaefc"))
        grad.setColorAt(1, QColor("#0073cc"))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(x, y, w, h), size*0.05, size*0.05)
        
        # Envelope flap
        flap = QPainterPath()
        flap.moveTo(x, y)
        flap.lineTo(size * 0.5, y + h * 0.55)
        flap.lineTo(x + w, y)
        
        painter.setPen(QPen(QColor("rgba(255, 255, 255, 0.4)"), size * 0.03))
        painter.setBrush(QBrush(QColor("rgba(255, 255, 255, 0.15)")))
        painter.drawPath(flap)
        
        # Small pigeon silhouette
        cls._draw_pigeon_shape(painter, size * 0.38, y + h * 0.45, size / 200.0, Qt.GlobalColor.white)

    @classmethod
    def _draw_calendar(cls, painter, size):
        w = size * 0.75
        h = size * 0.75
        x = (size - w) / 2
        y = (size - h) / 2
        
        # Base Calendar Grid (White)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRoundedRect(QRectF(x, y, w, h), size*0.06, size*0.06)
        
        # Red/Crimson Header
        header_height = h * 0.28
        header_path = QPainterPath()
        header_path.moveTo(x, y)
        header_path.lineTo(x + w, y)
        header_path.lineTo(x + w, y + header_height)
        header_path.lineTo(x, y + header_height)
        header_path.closeSubpath()
        
        painter.setBrush(QBrush(QColor("#f44336")))
        painter.drawPath(header_path)
        
        # Shadow or outline
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(x, y, w, h), size*0.06, size*0.06)
        
        # Draw some grid points representing days
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#888888")))
        dot_r = size * 0.04
        start_dx = x + w * 0.2
        start_dy = y + header_height + h * 0.2
        gap_x = w * 0.2
        gap_y = h * 0.2
        
        for row in range(3):
            for col in range(4):
                if row == 2 and col > 1:
                    continue # leave some empty
                painter.drawEllipse(QPointF(start_dx + col * gap_x, start_dy + row * gap_y), dot_r, dot_r)
                
        # Draw the big number 20 in the middle/right
        painter.setPen(QPen(QColor("#f44336")))
        font = painter.font()
        font.setPixelSize(int(size * 0.22))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(x, y + header_height, w, h - header_height), Qt.AlignmentFlag.AlignCenter, "20")

    @classmethod
    def _draw_photos(cls, painter, size):
        w = size * 0.75
        h = size * 0.65
        x = (size - w) / 2
        y = (size - h) / 2
        
        # Photo paper
        painter.setPen(QPen(QColor("#444"), size * 0.03))
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRoundedRect(QRectF(x, y, w, h), size*0.04, size*0.04)
        
        # Image background (sky-like)
        margin = size * 0.06
        img_rect = QRectF(x + margin, y + margin, w - 2*margin, h - 2*margin)
        painter.setPen(Qt.PenStyle.NoPen)
        grad = QLinearGradient(0, y, 0, y + h)
        grad.setColorAt(0, QColor("#a1c4fd"))
        grad.setColorAt(1, QColor("#c2e9fb"))
        painter.setBrush(QBrush(grad))
        painter.drawRect(img_rect)
        
        # Draw a little sun
        painter.setBrush(QBrush(QColor("#ffeb3b")))
        painter.drawEllipse(QPointF(x + w * 0.7, y + h * 0.3), size*0.06, size*0.06)
        
        # Draw small green pigeon mountains
        painter.setBrush(QBrush(QColor("#4caf50")))
        m1 = QPainterPath()
        m1.moveTo(x + margin, y + h - margin)
        m1.lineTo(x + w * 0.4, y + h * 0.5)
        m1.lineTo(x + w * 0.7, y + h - margin)
        m1.closeSubpath()
        painter.drawPath(m1)
        
        painter.setBrush(QBrush(QColor("#81c784")))
        m2 = QPainterPath()
        m2.moveTo(x + w * 0.3, y + h - margin)
        m2.lineTo(x + w * 0.65, y + h * 0.4)
        m2.lineTo(x + w - margin, y + h - margin)
        m2.closeSubpath()
        painter.drawPath(m2)

    @classmethod
    def _draw_settings(cls, painter, size):
        # Settings Gear
        cx = size * 0.5
        cy = size * 0.5
        r_outer = size * 0.32
        r_inner = size * 0.12
        
        painter.save()
        painter.translate(cx, cy)
        
        # Base gear circle
        painter.setPen(Qt.PenStyle.NoPen)
        grad = QLinearGradient(-r_outer, -r_outer, r_outer, r_outer)
        grad.setColorAt(0, QColor("#9aa0a6"))
        grad.setColorAt(1, QColor("#5f6368"))
        painter.setBrush(QBrush(grad))
        
        # Draw 8 teeth
        teeth = 8
        for i in range(teeth):
            painter.rotate(360 / teeth)
            rect = QRectF(-size * 0.07, -size * 0.4, size * 0.14, size * 0.2)
            painter.drawRoundedRect(rect, size*0.02, size*0.02)
            
        # Outer ring
        painter.drawEllipse(QPointF(0, 0), r_outer, r_outer)
        
        # Center hole (transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawEllipse(QPointF(0, 0), r_inner, r_inner)
        
        # Reset composition mode to draw the blue accent ring
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setPen(QPen(QColor("#0078d4"), size * 0.04))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0, 0), r_inner * 1.5, r_inner * 1.5)
        
        painter.restore()

    @classmethod
    def _draw_weather(cls, painter, size):
        # Sun & Cloud
        painter.save()
        
        # 1. Sun
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#ffb300")))
        painter.drawEllipse(QPointF(size * 0.65, size * 0.35), size*0.18, size*0.18)
        
        # 2. Cloud
        grad = QLinearGradient(0, size*0.4, 0, size*0.8)
        grad.setColorAt(0, QColor("#ffffff"))
        grad.setColorAt(1, QColor("#e0e0e0"))
        painter.setBrush(QBrush(grad))
        
        cloud = QPainterPath()
        cloud.moveTo(size * 0.2, size * 0.65)
        cloud.arcTo(QRectF(size*0.15, size*0.5, size*0.2, size*0.2), 90, 180)
        cloud.arcTo(QRectF(size*0.25, size*0.35, size*0.3, size*0.3), 120, 180)
        cloud.arcTo(QRectF(size*0.5, size*0.45, size*0.25, size*0.25), 0, 180)
        cloud.lineTo(size * 0.8, size * 0.7)
        cloud.lineTo(size * 0.2, size * 0.7)
        cloud.closeSubpath()
        
        painter.drawPath(cloud)
        painter.restore()

    @classmethod
    def _draw_terminal(cls, painter, size):
        w = size * 0.8
        h = size * 0.6
        x = (size - w) / 2
        y = (size - h) / 2
        
        # Terminal box
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#1e1e1e")))
        painter.drawRoundedRect(QRectF(x, y, w, h), size*0.05, size*0.05)
        
        # Text symbol >_
        painter.setPen(QPen(QColor("#4af626"), size * 0.04, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(x + size*0.1, y + size*0.15), QPointF(x + size*0.2, y + size*0.22))
        painter.drawLine(QPointF(x + size*0.2, y + size*0.22), QPointF(x + size*0.1, y + size*0.29))
        
        # Blinking cursor
        painter.drawLine(QPointF(x + size*0.24, y + size*0.29), QPointF(x + size*0.34, y + size*0.29))

    @classmethod
    def _draw_notepad(cls, painter, size):
        w = size * 0.7
        h = size * 0.8
        x = (size - w) / 2
        y = (size - h) / 2
        
        # Yellow Notepad Paper
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#fff9c4")))
        painter.drawRoundedRect(QRectF(x, y, w, h), size*0.04, size*0.04)
        
        # Red margin line
        painter.setPen(QPen(QColor("#ff8a80"), size * 0.02))
        painter.drawLine(QPointF(x + w * 0.18, y), QPointF(x + w * 0.18, y + h))
        
        # Blue notebook lines
        painter.setPen(QPen(QColor("#90caf9"), size * 0.015))
        line_y = y + h * 0.25
        while line_y < y + h * 0.85:
            painter.drawLine(QPointF(x + w * 0.2, line_y), QPointF(x + w * 0.9, line_y))
            line_y += h * 0.12
            
        # Draw a little pencil overlay
        painter.save()
        painter.translate(x + w*0.7, y + h*0.65)
        painter.rotate(-45)
        
        # Pencil body
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#ffb300")))
        painter.drawRect(0, 0, int(w*0.15), int(h*0.35))
        # Tip
        tip = QPainterPath()
        tip.moveTo(0, 0)
        tip.lineTo(w*0.075, -h*0.1)
        tip.lineTo(w*0.15, 0)
        tip.closeSubpath()
        painter.setBrush(QBrush(QColor("#ffe082")))
        painter.drawPath(tip)
        
        # Lead tip
        lead = QPainterPath()
        lead.moveTo(w*0.035, -h*0.05)
        lead.lineTo(w*0.075, -h*0.1)
        lead.lineTo(w*0.115, -h*0.05)
        lead.closeSubpath()
        painter.setBrush(QBrush(QColor("#424242")))
        painter.drawPath(lead)
        
        painter.restore()

    @classmethod
    def _draw_help(cls, painter, size):
        # Help question circle
        margin = size * 0.05
        rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
        
        grad = QLinearGradient(0, 0, 0, size)
        grad.setColorAt(0, QColor("#1e88e5"))
        grad.setColorAt(1, QColor("#1565c0"))
        
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)
        
        # Draw question mark
        painter.setPen(QPen(Qt.GlobalColor.white, size * 0.08, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        qpath = QPainterPath()
        qpath.arcMoveTo(QRectF(size*0.35, size*0.25, size*0.3, size*0.3), 180)
        qpath.arcTo(QRectF(size*0.35, size*0.25, size*0.3, size*0.3), 180, -220)
        qpath.quadTo(size*0.5, size*0.5, size*0.5, size*0.62)
        painter.drawPath(qpath)
        
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(size*0.5, size*0.75), size*0.05, size*0.05)

    @classmethod
    def _draw_recycle(cls, painter, size, empty=True):
        # Recycle Bin
        w = size * 0.65
        h = size * 0.75
        x = (size - w) / 2
        y = (size - h) / 2
        
        painter.setPen(QPen(QColor("#78909c"), size * 0.03))
        painter.setBrush(QBrush(QColor("rgba(240, 244, 250, 0.4)")))
        
        # Trash can outline
        bin_path = QPainterPath()
        bin_path.moveTo(x + w*0.1, y + h*0.2)
        bin_path.lineTo(x + w*0.15, y + h)
        bin_path.lineTo(x + w*0.85, y + h)
        bin_path.lineTo(x + w*0.9, y + h*0.2)
        bin_path.closeSubpath()
        painter.drawPath(bin_path)
        
        # Bin Lid
        painter.drawRoundedRect(QRectF(x + w*0.02, y + h*0.1, w*0.96, h*0.1), size*0.02, size*0.02)
        painter.drawRect(QRectF(x + w*0.35, y + h*0.05, w*0.3, h*0.05))
        
        # Vertical slats on bin
        painter.drawLine(QPointF(x + w*0.3, y + h*0.35), QPointF(x + w*0.33, y + h*0.9))
        painter.drawLine(QPointF(x + w*0.5, y + h*0.35), QPointF(x + w*0.5, y + h*0.9))
        painter.drawLine(QPointF(x + w*0.7, y + h*0.35), QPointF(x + w*0.67, y + h*0.9))
        
        if not empty:
            # Draw some crumpled trash paper inside
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#90a4ae")))
            
            p1 = QPainterPath()
            p1.moveTo(x + w*0.3, y + h*0.5)
            p1.lineTo(x + w*0.5, y + h*0.4)
            p1.lineTo(x + w*0.6, y + h*0.55)
            p1.lineTo(x + w*0.4, y + h*0.65)
            p1.closeSubpath()
            painter.drawPath(p1)
            
            painter.setBrush(QBrush(QColor("#cfd8dc")))
            p2 = QPainterPath()
            p2.moveTo(x + w*0.45, y + h*0.4)
            p2.lineTo(x + w*0.7, y + h*0.35)
            p2.lineTo(x + w*0.75, y + h*0.55)
            p2.lineTo(x + w*0.55, y + h*0.6)
            p2.closeSubpath()
            painter.drawPath(p2)

    @classmethod
    def _draw_drive(cls, painter, size, label="P"):
        w = size * 0.8
        h = size * 0.5
        x = (size - w) / 2
        y = (size - h) / 2
        
        # Hard drive case (Silver-blue)
        grad = QLinearGradient(0, y, 0, y+h)
        grad.setColorAt(0, QColor("#e0e6ed"))
        grad.setColorAt(1, QColor("#95a5b5"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#708090"), size*0.02))
        painter.drawRoundedRect(QRectF(x, y, w, h), size*0.04, size*0.04)
        
        # Dark panel details
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("rgba(30, 40, 50, 0.15)")))
        painter.drawRect(QRectF(x + w*0.08, y + h*0.15, w*0.84, h*0.4))
        
        # LED Light
        painter.setBrush(QBrush(QColor("#2ec27e")))
        painter.drawEllipse(QPointF(x + w*0.85, y + h*0.75), size*0.03, size*0.03)
        
        # Label text
        painter.setPen(QPen(QColor("#005fa3")))
        font = painter.font()
        font.setPixelSize(int(size * 0.2))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(x, y, w*0.7, h), Qt.AlignmentFlag.AlignCenter, label)

    @classmethod
    def _draw_cloud(cls, painter, size):
        w = size * 0.8
        h = size * 0.55
        x = (size - w) / 2
        y = (size - h) / 2
        
        grad = QLinearGradient(0, y, 0, y + h)
        grad.setColorAt(0, QColor("#72c6ff"))
        grad.setColorAt(1, QColor("#0073cc"))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        
        cloud = QPainterPath()
        cloud.moveTo(x + w*0.2, y + h*0.8)
        cloud.arcTo(QRectF(x + w*0.08, y + h*0.4, w*0.25, h*0.4), 90, 180)
        cloud.arcTo(QRectF(x + w*0.25, y + h*0.1, w*0.4, h*0.6), 120, 180)
        cloud.arcTo(QRectF(x + w*0.55, y + h*0.3, w*0.35, h*0.5), 0, 180)
        cloud.lineTo(x + w*0.9, y + h*0.8)
        cloud.lineTo(x + w*0.2, y + h*0.8)
        cloud.closeSubpath()
        painter.drawPath(cloud)
        
        # White wing overlay inside cloud
        cls._draw_wing_white(painter, size)

    @classmethod
    def _draw_file(cls, painter, size, text, color):
        w = size * 0.65
        h = size * 0.8
        x = (size - w) / 2
        y = (size - h) / 2
        
        # File document background (White/silver)
        painter.setPen(QPen(QColor("#cbd5e0"), size * 0.025))
        painter.setBrush(QBrush(QColor("#ffffff")))
        
        # Corner folded page
        fold = size * 0.18
        path = QPainterPath()
        path.moveTo(x, y + h)
        path.lineTo(x, y)
        path.lineTo(x + w - fold, y)
        path.lineTo(x + w, y + fold)
        path.lineTo(x + w, y + h)
        path.closeSubpath()
        painter.drawPath(path)
        
        # Draw the fold triangle
        fold_path = QPainterPath()
        fold_path.moveTo(x + w - fold, y)
        fold_path.lineTo(x + w - fold, y + fold)
        fold_path.lineTo(x + w, y + fold)
        fold_path.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#cbd5e0")))
        painter.drawPath(fold_path)
        
        # Color bar indicator
        painter.setBrush(QBrush(color))
        painter.drawRect(QRectF(x + w*0.15, y + h*0.65, w*0.7, h*0.12))
        
        # Draw text extension inside bar
        if text:
            painter.setPen(QPen(Qt.GlobalColor.white))
            font = painter.font()
            font.setPixelSize(int(size * 0.09))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRectF(x + w*0.15, y + h*0.65, w*0.7, h*0.12), Qt.AlignmentFlag.AlignCenter, text)
            
        # Draw minor text lines
        painter.setPen(QPen(QColor("#a0aec0"), size * 0.015))
        painter.drawLine(QPointF(x + w*0.15, y + h*0.25), QPointF(x + w*0.6, y + h*0.25))
        painter.drawLine(QPointF(x + w*0.15, y + h*0.38), QPointF(x + w*0.8, y + h*0.38))
        painter.drawLine(QPointF(x + w*0.15, y + h*0.51), QPointF(x + w*0.7, y + h*0.51))


is_dark_mode = False

def set_dark_mode(dark):
    global is_dark_mode
    is_dark_mode = dark

def get_stylesheet():
    if is_dark_mode:
        bg_window = "rgba(28, 33, 46, 0.9)"
        bg_window_inactive = "rgba(22, 26, 36, 0.95)"
        text = "#ffffff"
        text_muted = "#a0aec0"
        text_dark = "#ffffff"
        bg_sidebar = "rgba(20, 24, 33, 0.75)"
        bg_right_panel = "#1c1f26"
        bg_status_bar = "#16191f"
        bg_address_input = "#16191f"
        border_color = "rgba(255, 255, 255, 0.08)"
        border_light = "rgba(255, 255, 255, 0.15)"
        card_bg = "#242936"
        card_bg_hover = "#2c3242"
        card_border = "rgba(255, 255, 255, 0.08)"
        notepad_bg = "#1e1e24"
        notepad_text = "#e0e0e0"
        combo_bg = "#242936"
        combo_border = "rgba(255, 255, 255, 0.12)"
        input_bg = "#242936"
        input_border = "rgba(255, 255, 255, 0.12)"
        dialog_bg = "rgba(28, 33, 46, 0.98)"
        dialog_border = "rgba(255, 255, 255, 0.15)"
        scrollbar_handle = "rgba(255, 255, 255, 0.2)"
        scrollbar_handle_hover = "rgba(255, 255, 255, 0.4)"
        btn_bg = "#242936"
        btn_text = "#ffffff"
        btn_border = "rgba(255, 255, 255, 0.12)"
        btn_hover = "#2c3242"
    else:
        bg_window = "rgba(240, 244, 250, 0.9)"
        bg_window_inactive = "rgba(235, 238, 243, 0.95)"
        text = "#1a1f26"
        text_muted = "#606f7b"
        text_dark = "#1a1f26"
        bg_sidebar = "rgba(235, 240, 245, 0.75)"
        bg_right_panel = "#ffffff"
        bg_status_bar = "#f3f3f3"
        bg_address_input = "#f3f3f3"
        border_color = "rgba(0, 0, 0, 0.08)"
        border_light = "rgba(255, 255, 255, 0.4)"
        card_bg = "#ffffff"
        card_bg_hover = "#f7fafc"
        card_border = "rgba(0, 0, 0, 0.05)"
        notepad_bg = "#fffde7"
        notepad_text = "#37474f"
        combo_bg = "#ffffff"
        combo_border = "#d0d5dd"
        input_bg = "#ffffff"
        input_border = "#d0d5dd"
        dialog_bg = "rgba(240, 244, 250, 0.98)"
        dialog_border = "rgba(0, 0, 0, 0.12)"
        scrollbar_handle = "rgba(0, 0, 0, 0.15)"
        scrollbar_handle_hover = "rgba(0, 0, 0, 0.3)"
        btn_bg = "#ffffff"
        btn_text = "#2c3e50"
        btn_border = "#d0d5dd"
        btn_hover = "#f2f4f6"

    return f"""
    QMainWindow {{
        background-color: transparent;
    }}
    
    QWidget#desktop_workspace {{
        background-color: transparent;
    }}
    
    QFrame#sigeon_window_frame {{
        background-color: {bg_window};
        border: 1px solid {border_light};
        border-radius: 12px;
    }}
    
    QFrame#sigeon_window_frame_inactive {{
        background-color: {bg_window_inactive};
        border: 1px solid {border_light};
        border-radius: 12px;
    }}
    
    QWidget#titlebar_widget {{
        background-color: transparent;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
    }}
    
    QLabel#title_label {{
        font-family: 'Segoe UI', 'Segoe UI Variable', Helvetica, Arial, sans-serif;
        font-size: 12px;
        font-weight: 500;
        color: {text_dark};
    }}
    
    QPushButton#win_btn_close {{
        background-color: transparent;
        border-radius: 8px;
        border: none;
    }}
    QPushButton#win_btn_close:hover {{
        background-color: #e81123;
    }}
    
    QPushButton#win_btn_min, QPushButton#win_btn_max {{
        background-color: transparent;
        border-radius: 8px;
        border: none;
    }}
    QPushButton#win_btn_min:hover, QPushButton#win_btn_max:hover {{
        background-color: rgba({"255, 255, 255" if is_dark_mode else "0, 0, 0"}, 0.08);
    }}
    
    QPushButton#desktop_icon_btn {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
        padding: 5px;
    }}
    QPushButton#desktop_icon_btn:hover {{
        background-color: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
    }}
    QPushButton#desktop_icon_btn:focus {{
        background-color: rgba(255, 255, 255, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.4);
    }}
    
    QLabel#desktop_icon_label {{
        font-family: 'Segoe UI', Arial;
        font-size: 11px;
        color: #ffffff;
        font-weight: 500;
    }}
    
    QFrame#taskbar_frame {{
        background-color: rgba(24, 28, 38, 0.82);
        border-top: 1px solid rgba(255, 255, 255, 0.15);
    }}
    
    QPushButton#taskbar_pigeon_btn {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
        color: #ffffff;
        font-family: 'Segoe UI', Arial;
        font-size: 13px;
        font-weight: bold;
        padding: 0px 10px;
    }}
    QPushButton#taskbar_pigeon_btn:hover {{
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    QPushButton#taskbar_app_btn {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
        margin: 2px;
        padding: 4px;
    }}
    QPushButton#taskbar_app_btn:hover {{
        background-color: rgba(255, 255, 255, 0.08);
    }}
    QPushButton#taskbar_app_btn[active="true"] {{
        background-color: rgba(255, 255, 255, 0.12);
        border-bottom: 2px solid #0f82df;
    }}
    
    QFrame#start_menu_frame {{
        background-color: rgba(28, 33, 46, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
    }}
    
    QLineEdit#start_search_input {{
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px;
        color: #ffffff;
        padding: 6px 12px;
        font-size: 12px;
        selection-background-color: #0f82df;
    }}
    QLineEdit#start_search_input:focus {{
        border: 1px solid #0f82df;
        background-color: rgba(255, 255, 255, 0.12);
    }}
    
    QPushButton#start_app_grid_btn {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
        padding: 8px;
    }}
    QPushButton#start_app_grid_btn:hover {{
        background-color: rgba(255, 255, 255, 0.06);
    }}
    
    QLabel#start_app_grid_label {{
        color: #e0e6ed;
        font-size: 10px;
    }}
    
    QFrame#start_profile_section {{
        background-color: rgba(0, 0, 0, 0.2);
        border-bottom-left-radius: 11px;
        border-bottom-right-radius: 11px;
    }}
    
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 8px;
        margin: 2px 0 2px 0;
    }}
    QScrollBar::handle:vertical {{
        background: {scrollbar_handle};
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {scrollbar_handle_hover};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    
    QScrollBar:horizontal {{
        border: none;
        background: transparent;
        height: 8px;
        margin: 0 2px 0 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: {scrollbar_handle};
        min-width: 20px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {scrollbar_handle_hover};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}
    
    QWidget#explorer_sidebar {{
        background-color: {bg_sidebar};
        border-right: 1px solid {border_color};
        border-bottom-left-radius: 11px;
    }}
    
    QListWidget#explorer_sidebar_list {{
        background: transparent;
        border: none;
        outline: none;
    }}
    QListWidget#explorer_sidebar_list::item {{
        padding: 5px 8px;
        border-radius: 4px;
        color: {text};
        font-size: 11px;
        margin: 1px 4px;
    }}
    QListWidget#explorer_sidebar_list::item:hover {{
        background-color: rgba({"255, 255, 255" if is_dark_mode else "0, 0, 0"}, 0.04);
    }}
    QListWidget#explorer_sidebar_list::item:selected {{
        background-color: rgba(15, 130, 223, 0.12);
        color: #0f82df;
        font-weight: 500;
    }}
    
    QListWidget#explorer_folder_list {{
        background: transparent;
        border: none;
        outline: none;
    }}
    
    QTableWidget#explorer_recent_table {{
        background: transparent;
        border: none;
        gridline-color: transparent;
        outline: none;
    }}
    QTableWidget#explorer_recent_table QHeaderView::section {{
        background-color: transparent;
        border: none;
        color: {text_muted};
        font-size: 11px;
        padding-bottom: 4px;
    }}
    QTableWidget#explorer_recent_table::item {{
        border-bottom: 1px solid rgba({"255, 255, 255" if is_dark_mode else "0, 0, 0"}, 0.03);
        color: {text};
        font-size: 11px;
    }}
    QTableWidget#explorer_recent_table::item:selected {{
        background-color: rgba(15, 130, 223, 0.1);
        color: {text};
    }}
    
    QWidget#explorer_nav_bar {{
        background-color: {bg_right_panel};
        border-bottom: 1px solid {border_color};
    }}
    QWidget#explorer_right_panel {{
        background-color: {bg_right_panel};
    }}
    QWidget#explorer_status_bar {{
        background-color: {bg_status_bar};
        border-top: 1px solid {border_color};
    }}
    QLineEdit#explorer_address_input {{
        background-color: {bg_status_bar};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 11px;
        color: {text_muted};
    }}
    QLineEdit#explorer_search_input {{
        background-color: {bg_right_panel};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 11px;
        color: {text};
    }}
    
    QWidget#settings_sidebar {{
        background-color: {bg_sidebar};
        border-right: 1px solid {border_color};
        border-bottom-left-radius: 11px;
    }}
    
    QListWidget#settings_sidebar_list {{
        background: transparent;
        border: none;
        outline: none;
    }}
    QListWidget#settings_sidebar_list::item {{
        padding: 8px 12px;
        border-radius: 5px;
        color: {text};
        font-size: 12px;
        margin: 2px 6px;
    }}
    QListWidget#settings_sidebar_list::item:hover {{
        background-color: rgba({"255, 255, 255" if is_dark_mode else "0, 0, 0"}, 0.04);
    }}
    QListWidget#settings_sidebar_list::item:selected {{
        background-color: rgba(15, 130, 223, 0.15);
        color: #0f82df;
        font-weight: 600;
    }}
    
    QFrame#settings_card {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 8px;
    }}
    QFrame#settings_card:hover {{
        background-color: {card_bg_hover};
    }}
    
    QFrame#settings_item_card {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 8px;
    }}
    QFrame#settings_item_card:hover {{
        background-color: {card_bg_hover};
        border-color: rgba({"255, 255, 255" if is_dark_mode else "0, 0, 0"}, 0.08);
    }}
    
    QPushButton#settings_primary_btn {{
        background-color: #0f82df;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: bold;
        font-size: 11px;
    }}
    QPushButton#settings_primary_btn:hover {{
        background-color: #3fa5fc;
    }}
    QPushButton#settings_primary_btn:pressed {{
        background-color: #0060c0;
    }}
    
    QLabel#settings_page_title {{
        font-size: 20px;
        font-weight: bold;
        color: {text};
    }}
    QLabel#settings_section_hdr {{
        font-weight: bold;
        font-size: 13px;
        color: {text};
    }}
    QLabel#settings_label {{
        font-size: 11px;
        color: {text};
    }}
    QLabel#settings_val_label {{
        font-size: 11px;
        color: {text_muted};
    }}
    
    QTextEdit#terminal_history {{
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
        border: none;
    }}
    
    QLineEdit#terminal_input {{
        background-color: #1a1a1a;
        color: #4af626;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
        border: none;
        padding: 4px;
    }}
    
    QTextEdit#notepad_editor {{
        background-color: {notepad_bg};
        color: {notepad_text};
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        border: none;
    }}
    QWidget#notepad_toolbar {{
        background-color: {bg_status_bar};
        border-bottom: 1px solid {border_color};
    }}
    
    QLabel#weather_forecast_title {{
        font-size: 12px;
        font-weight: bold;
        color: {text};
    }}
    QFrame#forecast_card {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 6px;
        padding: 6px;
    }}
    QFrame#stat_card {{
        background-color: {card_bg_hover};
        border: 1px solid {card_border};
        border-radius: 6px;
        padding: 8px;
    }}
    
    QWidget#photos_viewer_panel {{
        background-color: {bg_right_panel};
    }}
    
    QDialog {{
        background-color: {dialog_bg};
        border: 1px solid {dialog_border};
        border-radius: 12px;
    }}
    QLineEdit {{
        background-color: {input_bg};
        border: 1px solid {input_border};
        border-radius: 5px;
        padding: 5px 8px;
        font-size: 12px;
        color: {text};
    }}
    QLineEdit:focus {{
        border: 1px solid #0f82df;
    }}
    QComboBox {{
        background-color: {combo_bg};
        border: 1px solid {combo_border};
        border-radius: 5px;
        padding: 4px 8px;
        font-size: 12px;
        color: {text};
    }}
    QComboBox:focus {{
        border: 1px solid #0f82df;
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {combo_bg};
        border: 1px solid {combo_border};
        selection-background-color: rgba(15, 130, 223, 0.15);
        selection-color: #0f82df;
        color: {text};
    }}
    QPushButton {{
        background-color: {btn_bg};
        border: 1px solid {btn_border};
        border-radius: 6px;
        padding: 5px 12px;
        font-size: 11px;
        color: {btn_text};
    }}
    QPushButton:hover {{
        background-color: {btn_hover};
    }}
    
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {bg_status_bar};
        border-bottom: 1px solid {border_color};
    }}
    QCalendarWidget QToolButton {{
        color: {text};
        background: transparent;
        border: none;
        border-radius: 4px;
        font-size: 11px;
        icon-size: 16px;
    }}
    QCalendarWidget QToolButton:hover {{
        background-color: {btn_hover};
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        color: {text};
        background-color: {bg_right_panel};
        selection-background-color: #0f82df;
        selection-color: #ffffff;
    }}
    QCalendarWidget QAbstractItemView:disabled {{
        color: {text_muted};
    }}
    
    QWidget#explorer_nav_bar {{
        background-color: {bg_status_bar};
        border-bottom: 1px solid {border_color};
    }}
    QWidget#explorer_right_panel {{
        background-color: {bg_right_panel};
    }}
    QWidget#explorer_status_bar {{
        background-color: {bg_status_bar};
        border-top: 1px solid {border_color};
    }}
    """
