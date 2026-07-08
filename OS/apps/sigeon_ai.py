import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QUrl, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QBrush, QRadialGradient, QFont, QLinearGradient

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False

AI_URL = "https://pigeon-spark-ai.lovable.app/"


class PulsingOrb(QWidget):
    """Animated glowing orb used in the splash screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        self._pulse = 0.0
        self._direction = 1

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(20)

    def _tick(self):
        self._pulse += 0.025 * self._direction
        if self._pulse >= 1.0:
            self._direction = -1
        elif self._pulse <= 0.0:
            self._direction = 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy, r = 90, 90, 70

        # Outer glow
        for i in range(4, 0, -1):
            glow_r = r + i * 12 * (0.4 + self._pulse * 0.6)
            alpha = int(30 * (1 - i / 5) * (0.5 + self._pulse * 0.5))
            grad = QRadialGradient(cx, cy, glow_r)
            grad.setColorAt(0.0, QColor(160, 80, 255, alpha))
            grad.setColorAt(0.5, QColor(80, 180, 255, alpha // 2))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(cx - glow_r), int(cy - glow_r),
                          int(glow_r * 2), int(glow_r * 2))

        # Core orb
        core_grad = QRadialGradient(cx - 20, cy - 20, r * (0.85 + self._pulse * 0.15))
        core_grad.setColorAt(0.0, QColor(220, 160, 255, 255))
        core_grad.setColorAt(0.4, QColor(120, 80, 255, 240))
        core_grad.setColorAt(0.7, QColor(60, 120, 255, 220))
        core_grad.setColorAt(1.0, QColor(20, 60, 180, 200))
        p.setBrush(QBrush(core_grad))
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Shine highlight
        shine_grad = QRadialGradient(cx - 25, cy - 28, 30)
        shine_grad.setColorAt(0.0, QColor(255, 255, 255, 160))
        shine_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(shine_grad))
        p.drawEllipse(cx - 50, cy - 55, 60, 50)
        p.end()


class SigeonAISplash(QWidget):
    """Shown while the WebEngine loads."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self.orb = PulsingOrb(self)
        self.orb.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        orb_row = QHBoxLayout()
        orb_row.addStretch()
        orb_row.addWidget(self.orb)
        orb_row.addStretch()
        layout.addLayout(orb_row)

        self.title = QLabel("SigeonAI")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 26, QFont.Weight.Bold)
        self.title.setFont(font)
        self.title.setStyleSheet("color: #d0a0ff; letter-spacing: 2px;")
        layout.addWidget(self.title)

        self.subtitle = QLabel("Connecting to AI…")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("color: rgba(200,180,255,0.6); font-size: 12px;")
        layout.addWidget(self.subtitle)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(18, 8, 38))
        grad.setColorAt(0.5, QColor(28, 10, 55))
        grad.setColorAt(1.0, QColor(12, 5, 28))
        p.fillRect(0, 0, w, h, QBrush(grad))

        # Ambient glow blobs
        for cx, cy, r, col in [
            (w * 0.2, h * 0.3, 200, QColor(100, 40, 200, 40)),
            (w * 0.8, h * 0.6, 250, QColor(40, 100, 220, 30)),
            (w * 0.5, h * 0.8, 180, QColor(160, 60, 255, 25)),
        ]:
            bg = QRadialGradient(cx, cy, r)
            bg.setColorAt(0.0, col)
            bg.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(bg))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))

        p.end()


class SigeonAIApp(QWidget):
    """SigeonAI – an embedded AI assistant powered by pigeon-spark-ai."""

    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.setMinimumSize(800, 560)
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #1a0840, stop:0.5 #2d0e6e, stop:1 #1a0840);"
            "border-bottom: 1px solid rgba(180,100,255,0.25);"
        )
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(14, 0, 14, 0)
        hlay.setSpacing(10)

        orb_dot = QLabel("🤖")
        orb_dot.setStyleSheet("font-size: 22px;")
        hlay.addWidget(orb_dot)

        title_lbl = QLabel("SigeonAI")
        title_lbl.setStyleSheet(
            "color: #d0a0ff; font-size: 15px; font-weight: bold; letter-spacing: 1px;"
        )
        hlay.addWidget(title_lbl)

        badge = QLabel("POWERED BY PIGEON SPARK")
        badge.setStyleSheet(
            "color: rgba(180,120,255,0.7); font-size: 8px; font-weight: bold;"
            " letter-spacing: 2px; margin-top: 3px;"
        )
        hlay.addWidget(badge)
        hlay.addStretch()

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #ffaa33; font-size: 10px;")
        hlay.addWidget(self.status_dot)

        self.status_lbl = QLabel("Connecting…")
        self.status_lbl.setStyleSheet("color: rgba(200,180,255,0.6); font-size: 10px;")
        hlay.addWidget(self.status_lbl)

        reload_btn = QPushButton("↻")
        reload_btn.setFixedSize(28, 28)
        reload_btn.setStyleSheet(
            "QPushButton { color: #c0a0ff; background: rgba(180,100,255,0.12);"
            " border: 1px solid rgba(180,100,255,0.2); border-radius: 6px; font-size: 14px; }"
            "QPushButton:hover { background: rgba(180,100,255,0.25); }"
        )
        reload_btn.clicked.connect(self._reload)
        hlay.addWidget(reload_btn)

        root.addWidget(header)

        # ── Content area (web or fallback) ─────────────────────────────────
        if WEB_ENGINE_AVAILABLE:
            self.splash = SigeonAISplash(self)
            root.addWidget(self.splash)

            self.web = QWebEngineView()

            # Customise the web profile so pages see a modern browser UA
            profile = QWebEngineProfile.defaultProfile()
            profile.setHttpUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36 SigeonOS/7.0"
            )

            # Enable all necessary web settings
            settings = self.web.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

            self.web.setUrl(QUrl(AI_URL))
            self.web.hide()  # Hidden until loaded
            root.addWidget(self.web)

            self.web.loadStarted.connect(self._on_load_start)
            self.web.loadProgress.connect(self._on_load_progress)
            self.web.loadFinished.connect(self._on_load_finished)

        else:
            err = QLabel(
                "⚠️  WebEngine not available.\n\n"
                "Install PyQt6-WebEngine to use SigeonAI.\n\n"
                "pip install PyQt6-WebEngine"
            )
            err.setAlignment(Qt.AlignmentFlag.AlignCenter)
            err.setStyleSheet(
                "background: #100826; color: #c0a0ff;"
                " font-size: 14px; padding: 40px;"
            )
            root.addWidget(err)
            self.web = None

    # ── Slots ──────────────────────────────────────────────────────────────
    def _on_load_start(self):
        self.status_dot.setStyleSheet("color: #ffaa33; font-size: 10px;")
        self.status_lbl.setText("Loading…")

    def _on_load_progress(self, pct: int):
        self.status_lbl.setText(f"Loading… {pct}%")

    def _on_load_finished(self, ok: bool):
        if ok:
            self.status_dot.setStyleSheet("color: #50fa7b; font-size: 10px;")
            self.status_lbl.setText("Connected")
            # Fade out splash and show web
            self._show_web()
        else:
            self.status_dot.setStyleSheet("color: #ff5555; font-size: 10px;")
            self.status_lbl.setText("Connection failed")
            self._show_web()  # show web anyway (it may have a partial page)

    def _show_web(self):
        if hasattr(self, 'splash') and self.splash.isVisible():
            # Quick fade out
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            effect = QGraphicsOpacityEffect(self.splash)
            self.splash.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(400)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.finished.connect(lambda: (self.splash.hide(), self.web.show()))
            anim.start()
            self._fade_anim = anim  # keep reference
        else:
            if self.web:
                self.web.show()

    def _reload(self):
        if self.web:
            if hasattr(self, 'splash'):
                self.splash.show()
                self.web.hide()
            self.web.reload()
