import sys
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QKeyEvent

class FlappyPigeonGame(QWidget):
    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.init_game_state()
        
        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_tick)
        
        self.setMinimumSize(400, 300)

    def init_game_state(self):
        self.pigeon_y = 150.0
        self.pigeon_vel = 0.0
        self.gravity = 0.4
        self.flap_strength = -6.5
        self.pigeon_x = 80.0
        self.pigeon_radius = 12.0
        
        self.pipes = [] # Items: [x, gap_y, gap_height]
        self.pipe_width = 50.0
        self.pipe_speed = 3.0
        self.pipe_gap = 90.0
        self.pipe_spawn_time = 0
        
        self.score = 0
        self.game_over = False
        self.game_started = False

    def spawn_pipe(self):
        gap_y = random.randint(50, self.height() - 150)
        self.pipes.append([float(self.width()), float(gap_y), self.pipe_gap])

    def game_tick(self):
        if not self.game_started or self.game_over:
            return
            
        # Physics
        self.pigeon_vel += self.gravity
        self.pigeon_y += self.pigeon_vel
        
        # Spawn pipes
        self.pipe_spawn_time += 1
        if self.pipe_spawn_time > 70:
            self.spawn_pipe()
            self.pipe_spawn_time = 0
            
        # Move pipes
        for pipe in self.pipes:
            pipe[0] -= self.pipe_speed
            
        # Remove offscreen pipes
        if self.pipes and self.pipes[0][0] < -self.pipe_width:
            self.pipes.pop(0)
            self.score += 1
            
        # Collision Check
        if self.pigeon_y - self.pigeon_radius < 0 or self.pigeon_y + self.pigeon_radius > self.height():
            self.end_game()
            
        p_rect = QRectF(self.pigeon_x - self.pigeon_radius, self.pigeon_y - self.pigeon_radius, 
                        self.pigeon_radius * 2, self.pigeon_radius * 2)
                        
        for pipe_x, gap_y, gap_h in self.pipes:
            top_pipe = QRectF(pipe_x, 0, self.pipe_width, gap_y)
            bot_pipe = QRectF(pipe_x, gap_y + gap_h, self.pipe_width, self.height() - (gap_y + gap_h))
            
            if p_rect.intersects(top_pipe) or p_rect.intersects(bot_pipe):
                self.end_game()
                
        self.update()

    def end_game(self):
        self.game_over = True
        self.timer.stop()
        self.update()

    def jump(self):
        if self.game_over:
            self.init_game_state()
            self.game_started = True
            self.timer.start(16) # ~60fps
        elif not self.game_started:
            self.game_started = True
            self.timer.start(16)
            self.pigeon_vel = self.flap_strength
        else:
            self.pigeon_vel = self.flap_strength
        self.update()

    # Inputs
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.jump()
            event.accept()

    def mousePressEvent(self, event):
        self.jump()
        event.accept()

    # Render
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Sky background
        painter.setBrush(QBrush(QColor("#a1c4fd")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())
        
        # Draw Pipes
        painter.setBrush(QBrush(QColor("#2ecc71")))
        painter.setPen(QPen(QColor("#27ae60"), 2))
        for pipe_x, gap_y, gap_h in self.pipes:
            # Top Pipe
            painter.drawRect(QRectF(pipe_x, -2, self.pipe_width, gap_y + 2))
            # Bottom Pipe
            painter.drawRect(QRectF(pipe_x, gap_y + gap_h, self.pipe_width, self.height() - (gap_y + gap_h) + 2))
            
        # Draw Pigeon
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#ffffff")))
        # Head & Body
        painter.drawEllipse(QPointF(self.pigeon_x, self.pigeon_y), self.pigeon_radius, self.pigeon_radius * 0.9)
        painter.drawEllipse(QPointF(self.pigeon_x + 6, self.pigeon_y - 6), 6, 6) # head
        
        # Beak
        painter.setBrush(QBrush(QColor("#e67e22")))
        beak = [QPointF(self.pigeon_x + 11, self.pigeon_y - 8),
                QPointF(self.pigeon_x + 16, self.pigeon_y - 6),
                QPointF(self.pigeon_x + 11, self.pigeon_y - 4)]
        painter.drawPolygon(beak)
        
        # Wing
        painter.setBrush(QBrush(QColor("#72c6ff")))
        painter.drawEllipse(QPointF(self.pigeon_x - 3, self.pigeon_y + 1), 6, 4)
        
        # Eye
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawEllipse(QPointF(self.pigeon_x + 6, self.pigeon_y - 7), 1.2, 1.2)
        
        # UI Overlays
        painter.setPen(QPen(QColor("#ffffff")))
        font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        painter.setFont(font)
        
        if not self.game_started:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Press SPACE or CLICK to fly! 🕊️")
        elif self.game_over:
            font.setPointSize(16)
            painter.setFont(font)
            painter.setPen(QPen(QColor("#c0392b")))
            painter.drawText(QRectF(0, self.height()*0.3, self.width(), 40), Qt.AlignmentFlag.AlignCenter, "GAME OVER")
            
            font.setPointSize(12)
            painter.setFont(font)
            painter.setPen(QPen(QColor("#2c3e50")))
            painter.drawText(QRectF(0, self.height()*0.45, self.width(), 30), Qt.AlignmentFlag.AlignCenter, f"Score: {self.score}")
            painter.drawText(QRectF(0, self.height()*0.58, self.width(), 30), Qt.AlignmentFlag.AlignCenter, "Click to restart")
        else:
            # Draw live score
            painter.drawText(QRectF(20, 20, 100, 30), Qt.AlignmentFlag.AlignLeft, f"Score: {self.score}")
