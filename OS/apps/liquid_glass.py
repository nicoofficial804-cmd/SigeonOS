import sys
import os
import math
import random
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient, QFont, QMouseEvent, QPainterPath

try:
    import psutil
except ImportError:
    psutil = None

class LiquidBubble:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vy = -random.uniform(1.0, 2.5) # Float upwards
        self.vx = random.uniform(-0.5, 0.5)
        self.wobble_speed = random.uniform(0.05, 0.15)
        self.wobble_amplitude = random.uniform(2, 6)
        self.wobble_phase = random.uniform(0, 2 * math.pi)
        self.life = 1.0 # Decay factor for fading out

    def update(self):
        self.y += self.vy
        self.wobble_phase += self.wobble_speed
        self.x += self.vx + math.sin(self.wobble_phase) * 0.1
        self.life -= 0.008

class SigeonLiquidGlassWidget(QWidget):
    """
    A stunning, interactive floating widget utilizing glassmorphism and liquid physics.
    Displays Time/Date and system diagnostics (CPU/RAM) as beautifully animated fluid.
    Drag to reposition. Interactive with mouse hover and click.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.SubWindow)
        self.setFixedSize(260, 280)
        self.setObjectName("liquid_glass_card")
        
        self.drag_position = QPoint()
        self.is_dragging = False
        
        # Color schemes for the liquid fluid
        self.color_schemes = [
            # Cyan & Blue
            (QColor("#00F2FE"), QColor("#4FACFE"), QColor("rgba(0, 242, 254, 0.25)")),
            # Magenta & Violet
            (QColor("#F35588"), QColor("#7000FF"), QColor("rgba(243, 85, 136, 0.25)")),
            # Emerald & Lime
            (QColor("#05DFD7"), QColor("#A3DE83"), QColor("rgba(5, 223, 215, 0.25)")),
            # Sunset Gold & Red
            (QColor("#F6D365"), QColor("#FDA085"), QColor("rgba(246, 211, 101, 0.25)")),
        ]
        self.current_scheme_idx = 0
        
        # Animation & Physics State
        self.wave_phase = 0.0
        self.bubbles = []
        self.cpu_level = 0.35
        self.ram_level = 0.45
        self.target_cpu = 0.35
        self.target_ram = 0.45
        
        # Diagnostics Update Timer
        self.diag_timer = QTimer(self)
        self.diag_timer.timeout.connect(self.update_diagnostics)
        self.diag_timer.start(2000) # Every 2s
        
        # Physics / Wave Animation Timer (60 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(16)
        
        # Apply drop shadow for the premium glass floating effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        # Setup Mouse Tracking for hover bubbles
        self.setMouseTracking(True)
        self.last_mouse_pos = QPointF()

    def update_diagnostics(self):
        if psutil:
            try:
                self.target_cpu = psutil.cpu_percent() / 100.0
                self.target_ram = psutil.virtual_memory().percent / 100.0
            except:
                pass
        else:
            # Simulate natural fluctuation
            self.target_cpu = 0.20 + 0.30 * math.sin(time.time() * 0.1) + random.uniform(-0.05, 0.05)
            self.target_ram = 0.40 + 0.15 * math.cos(time.time() * 0.05)
            
        self.target_cpu = max(0.05, min(0.95, self.target_cpu))
        self.target_ram = max(0.05, min(0.95, self.target_ram))

    def animate(self):
        # Smooth interpolation to target diagnostics
        self.cpu_level += (self.target_cpu - self.cpu_level) * 0.05
        self.ram_level += (self.target_ram - self.ram_level) * 0.05
        
        # Advance fluid wave phase
        self.wave_phase += 0.04
        
        # Update particles/bubbles
        active_bubbles = []
        for b in self.bubbles:
            b.update()
            if b.life > 0 and b.y > 60: # Keep inside liquid bounds
                active_bubbles.append(b)
        self.bubbles = active_bubbles
        
        # Occasionally spawn background ambient micro-bubbles
        if random.random() < 0.15:
            # Spawn near the bottom of the liquid container
            colors = self.color_schemes[self.current_scheme_idx]
            x_pos = random.uniform(25, self.width() - 25)
            # Y position based on current average level
            avg_level_y = self.height() - 40
            b_radius = random.uniform(2, 5)
            self.bubbles.append(LiquidBubble(x_pos, avg_level_y, b_radius, colors[0]))
            
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on the color switch zone (top-right circular button area)
            local_pos = event.position()
            if local_pos.x() > self.width() - 35 and local_pos.y() < 35:
                # Cycle color scheme!
                self.current_scheme_idx = (self.current_scheme_idx + 1) % len(self.color_schemes)
                self.spawn_burst(self.width() - 20, 20, 20)
                self.update()
                event.accept()
                return
                
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()
            
            # Spawn interactive bubbles on click
            self.spawn_burst(local_pos.x(), local_pos.y(), 10)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            parent = self.parentWidget()
            if parent:
                new_pos = event.globalPosition().toPoint() - self.drag_position
                # Restrict to parent widget borders
                new_pos.setX(max(0, min(parent.width() - self.width(), new_pos.x())))
                new_pos.setY(max(0, min(parent.height() - self.height(), new_pos.y())))
                self.move(new_pos)
            event.accept()
        else:
            # Mouse hover tracking -> spawn tiny bubbles trailing the cursor inside liquid
            local_pos = event.position()
            avg_y = self.height() - 70 # average liquid height boundary
            if local_pos.y() > avg_y:
                self.last_mouse_pos = local_pos
                if random.random() < 0.4:
                    colors = self.color_schemes[self.current_scheme_idx]
                    self.bubbles.append(LiquidBubble(
                        local_pos.x() + random.uniform(-4, 4),
                        local_pos.y() + random.uniform(-4, 4),
                        random.uniform(3, 7),
                        colors[0]
                    ))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.is_dragging = False
        super().mouseReleaseEvent(event)

    def spawn_burst(self, x, y, count):
        colors = self.color_schemes[self.current_scheme_idx]
        for _ in range(count):
            rad = random.uniform(3, 8)
            b = LiquidBubble(x + random.uniform(-10, 10), y + random.uniform(-10, 10), rad, colors[1])
            # Modify velocity for explosion look
            b.vx = random.uniform(-2.0, 2.0)
            b.vy = random.uniform(-3.5, -0.5)
            self.bubbles.append(b)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # 1. Base Glassmorphism Container background
        # Semi-transparent dark/acrylic panel
        glass_path = QPainterPath()
        glass_path.addRoundedRect(QRectF(0, 0, w, h), 24, 24)
        
        painter.save()
        painter.setClipPath(glass_path)
        
        # Subtle dark frosted glass backfill
        painter.setBrush(QBrush(QColor("rgba(15, 20, 32, 0.45)")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, w, h)
        
        # Linear light shine sheen from top-left to bottom-right
        sheen_grad = QLinearGradient(0, 0, w, h)
        sheen_grad.setColorAt(0.0, QColor("rgba(255, 255, 255, 0.08)"))
        sheen_grad.setColorAt(0.4, QColor("rgba(255, 255, 255, 0.0)"))
        sheen_grad.setColorAt(0.8, QColor("rgba(255, 255, 255, 0.03)"))
        sheen_grad.setColorAt(1.0, QColor("rgba(255, 255, 255, 0.06)"))
        painter.setBrush(QBrush(sheen_grad))
        painter.drawRect(0, 0, w, h)
        
        # Get active colors
        color_start, color_end, color_bg = self.color_schemes[self.current_scheme_idx]
        
        # 2. Draw Diagnostic Glass Tanks (CPU & RAM)
        # Left Tank: CPU, Right Tank: RAM
        tank_width = 85
        tank_height = 130
        tank_y = 115
        
        tanks = [
            (30, self.cpu_level, "CPU", f"{int(self.cpu_level * 100)}%"),
            (145, self.ram_level, "RAM", f"{int(self.ram_level * 100)}%")
        ]
        
        for tx, level, label, val_text in tanks:
            # Draw Glass Tank Backing
            tank_rect = QRectF(tx, tank_y, tank_width, tank_height)
            tank_path = QPainterPath()
            tank_path.addRoundedRect(tank_rect, 14, 14)
            
            painter.save()
            painter.setClipPath(tank_path)
            
            # Dark backing inside tank
            painter.setBrush(QBrush(QColor("rgba(0, 0, 0, 0.3)")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(tx, tank_y, tank_width, tank_height)
            
            # Draw Waves for Fluid Liquid
            fill_height = tank_height * level
            liquid_top = tank_y + tank_height - fill_height
            
            wave_path = QPainterPath()
            wave_path.moveTo(tx, tank_y + tank_height)
            wave_path.lineTo(tx, liquid_top)
            
            # Draw double wave curves for rich look
            steps = 40
            for i in range(steps + 1):
                px = tx + (tank_width / steps) * i
                # Create rolling wave formula
                wave_offset = math.sin(self.wave_phase + (i * 0.1) + (tx * 0.05)) * 4.0
                py = liquid_top + wave_offset
                wave_path.lineTo(px, py)
                
            wave_path.lineTo(tx + tank_width, tank_y + tank_height)
            wave_path.closeSubpath()
            
            # Gradient fill for liquid
            liq_grad = QLinearGradient(tx, tank_y + tank_height, tx, tank_y + tank_height - tank_height)
            liq_grad.setColorAt(0.0, color_end)
            liq_grad.setColorAt(0.8, color_start)
            # Specular glow top highlight
            liq_grad.setColorAt(1.0, QColor("#FFFFFF"))
            
            painter.setBrush(QBrush(liq_grad))
            painter.drawPath(wave_path)
            
            # Secondary ambient/slower wave behind (semi-transparent)
            back_wave_path = QPainterPath()
            back_wave_path.moveTo(tx, tank_y + tank_height)
            back_wave_path.lineTo(tx, liquid_top)
            for i in range(steps + 1):
                px = tx + (tank_width / steps) * i
                wave_offset2 = math.cos(-self.wave_phase * 0.8 + (i * 0.12)) * 3.5
                py = liquid_top + wave_offset2 - 2
                back_wave_path.lineTo(px, py)
            back_wave_path.lineTo(tx + tank_width, tank_y + tank_height)
            back_wave_path.closeSubpath()
            
            painter.setBrush(QBrush(QColor(color_bg.red(), color_bg.green(), color_bg.blue(), 100)))
            painter.drawPath(back_wave_path)
            
            # Restore clip to draw tank border
            painter.restore()
            
            # Draw Tank Glass Rim/Highlight
            rim_pen = QPen(QColor("rgba(255, 255, 255, 0.18)"), 1.5)
            painter.setPen(rim_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(tank_rect, 14, 14)
            
            # Specular light reflex on tank edge
            sheen_pen = QPen(QColor("rgba(255, 255, 255, 0.4)"), 1)
            painter.setPen(sheen_pen)
            painter.drawPath(self.create_top_left_rim(tank_rect, 14))
            
            # Diagnostic Text Labels inside Tank
            # Label
            font_label = QFont("Segoe UI", 10, QFont.Weight.Medium)
            painter.setFont(font_label)
            painter.setPen(QColor("rgba(255, 255, 255, 0.8)"))
            painter.drawText(QRectF(tx, tank_y + 12, tank_width, 20), Qt.AlignmentFlag.AlignCenter, label)
            
            # Value
            font_val = QFont("Segoe UI", 13, QFont.Weight.Bold)
            painter.setFont(font_val)
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(QRectF(tx, tank_y + tank_height - 28, tank_width, 24), Qt.AlignmentFlag.AlignCenter, val_text)
            
        # 3. Draw Interactive Physics Bubbles inside tanks
        for b in self.bubbles:
            # Radial bubble glow
            bub_grad = QRadialGradient(b.x, b.y, b.radius, b.x - b.radius * 0.2, b.y - b.radius * 0.2)
            bub_grad.setColorAt(0.0, QColor(255, 255, 255, int(255 * b.life)))
            bub_grad.setColorAt(0.5, QColor(b.color.red(), b.color.green(), b.color.blue(), int(180 * b.life)))
            bub_grad.setColorAt(1.0, QColor(b.color.red(), b.color.green(), b.color.blue(), 0))
            
            painter.setBrush(QBrush(bub_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(b.x, b.y), b.radius, b.radius)
            
            # Mini white reflection dot on the bubble
            painter.setBrush(QBrush(QColor(255, 255, 255, int(150 * b.life))))
            painter.drawEllipse(QPointF(b.x - b.radius*0.3, b.y - b.radius*0.3), b.radius*0.2, b.radius*0.2)

        # 4. Top section: Time & Date header
        # Get current time
        t_struct = time.localtime()
        time_str = time.strftime("%H:%M", t_struct)
        date_str = time.strftime("%A, %b %d", t_struct)
        
        # Digital Clock
        font_clock = QFont("Segoe UI", 26, QFont.Weight.ExtraBold)
        painter.setFont(font_clock)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(QRectF(15, 12, w - 30, 40), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, time_str)
        
        # Date
        font_date = QFont("Segoe UI", 10, QFont.Weight.Medium)
        painter.setFont(font_date)
        painter.setPen(QColor("rgba(255, 255, 255, 0.65)"))
        painter.drawText(QRectF(15, 50, w - 30, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, date_str)
        
        # 5. Paint Color Swap Button in Top-Right
        btn_center = QPointF(w - 20, 20)
        painter.setBrush(QBrush(color_start))
        painter.setPen(QPen(QColor("rgba(255, 255, 255, 0.6)"), 1))
        painter.drawEllipse(btn_center, 7, 7)
        
        # White glowing ring
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("rgba(255, 255, 255, 0.25)"), 1))
        painter.drawEllipse(btn_center, 11, 11)

        painter.restore()
        
        # 6. Outer Glass Card Border & Reflection Highlight
        border_pen = QPen(QColor("rgba(255, 255, 255, 0.15)"), 1.5)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(0, 0, w, h), 24, 24)
        
        # Highlight top & left edges (realistic specular glass reflection)
        highlight_pen = QPen(QColor("rgba(255, 255, 255, 0.45)"), 1)
        painter.setPen(highlight_pen)
        painter.drawPath(self.create_top_left_rim(QRectF(0, 0, w, h), 24))

    def create_top_left_rim(self, rect: QRectF, radius: float) -> QPainterPath:
        path = QPainterPath()
        # Draw from bottom-left up, around the top-left corner, to the top-right
        path.moveTo(rect.x(), rect.y() + rect.height() - radius)
        path.lineTo(rect.x(), rect.y() + radius)
        path.arcTo(rect.x(), rect.y(), radius * 2, radius * 2, 180, -90)
        path.lineTo(rect.x() + rect.width() - radius, rect.y())
        return path
