import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLineEdit, QLabel, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QColor
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineProfile
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
import theme


class SigeonBrowser(QWidget):
    """SigeonOS built-in web browser – Feather Browser."""

    def __init__(self, desktop_parent=None, url: str = "https://www.google.com"):
        super().__init__()
        self.desktop = desktop_parent
        self._start_url = url
        self.init_ui()

    # ------------------------------------------------------------------ UI --
    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Navigation bar ──────────────────────────────────────────────────
        nav = QWidget()
        nav.setFixedHeight(44)
        nav.setStyleSheet(
            "background: #1e1e2e;"
            "border-bottom: 1px solid rgba(255,255,255,0.08);"
        )
        nav_lay = QHBoxLayout(nav)
        nav_lay.setContentsMargins(8, 0, 8, 0)
        nav_lay.setSpacing(6)

        btn_style = (
            "QPushButton {"
            "  background: rgba(255,255,255,0.06);"
            "  color: #cdd6f4;"
            "  border: none;"
            "  border-radius: 6px;"
            "  font-size: 15px;"
            "  padding: 4px 10px;"
            "}"
            "QPushButton:hover { background: rgba(255,255,255,0.14); }"
            "QPushButton:disabled { color: rgba(205,214,244,0.3); }"
        )

        self.btn_back = QPushButton("←")
        self.btn_back.setFixedSize(34, 28)
        self.btn_back.setStyleSheet(btn_style)
        self.btn_back.clicked.connect(self._go_back)
        nav_lay.addWidget(self.btn_back)

        self.btn_forward = QPushButton("→")
        self.btn_forward.setFixedSize(34, 28)
        self.btn_forward.setStyleSheet(btn_style)
        self.btn_forward.clicked.connect(self._go_forward)
        nav_lay.addWidget(self.btn_forward)

        self.btn_reload = QPushButton("↻")
        self.btn_reload.setFixedSize(34, 28)
        self.btn_reload.setStyleSheet(btn_style)
        self.btn_reload.clicked.connect(self._reload)
        nav_lay.addWidget(self.btn_reload)

        self.btn_home = QPushButton("⌂")
        self.btn_home.setFixedSize(34, 28)
        self.btn_home.setStyleSheet(btn_style)
        self.btn_home.clicked.connect(self._go_home)
        nav_lay.addWidget(self.btn_home)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address…")
        self.url_bar.setStyleSheet(
            "QLineEdit {"
            "  background: rgba(255,255,255,0.09);"
            "  color: #cdd6f4;"
            "  border: 1px solid rgba(255,255,255,0.12);"
            "  border-radius: 8px;"
            "  padding: 4px 12px;"
            "  font-size: 12px;"
            "  selection-background-color: #89b4fa;"
            "}"
            "QLineEdit:focus { border: 1px solid #89b4fa; }"
        )
        self.url_bar.returnPressed.connect(self._navigate_to_url)
        nav_lay.addWidget(self.url_bar, stretch=1)

        # Security indicator
        self.lock_label = QLabel("🔒")
        self.lock_label.setStyleSheet("color: #a6e3a1; font-size: 14px; padding: 0 4px;")
        nav_lay.addWidget(self.lock_label)

        root.addWidget(nav)

        # ── Progress bar ────────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { background: transparent; border: none; }"
            "QProgressBar::chunk { background: #89b4fa; border-radius: 1px; }"
        )
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        root.addWidget(self.progress_bar)

        # ── Web view ────────────────────────────────────────────────────────
        if WEB_ENGINE_AVAILABLE:
            self.web = QWebEngineView()
            self.web.setUrl(QUrl(self._start_url))
            root.addWidget(self.web, stretch=1)
        else:
            self.web = None
            self.web_error = QLabel("WebEngine not installed.\nPlease install 'PyQt6-WebEngine' to use Feather Browser.")
            self.web_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.web_error.setStyleSheet("color: #f38ba8; font-size: 14px; background: #1e1e2e;")
            root.addWidget(self.web_error, stretch=1)

        # ── Status bar ──────────────────────────────────────────────────────
        status = QWidget()
        status.setFixedHeight(20)
        status.setStyleSheet(
            "background: #181825;"
            "border-top: 1px solid rgba(255,255,255,0.05);"
        )
        status_lay = QHBoxLayout(status)
        status_lay.setContentsMargins(10, 0, 10, 0)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: rgba(205,214,244,0.5); font-size: 10px;")
        status_lay.addWidget(self.status_label)
        status_lay.addStretch()

        self.page_label = QLabel("")
        self.page_label.setStyleSheet("color: rgba(205,214,244,0.35); font-size: 10px;")
        status_lay.addWidget(self.page_label)

        root.addWidget(status)

        # ── Connect web signals ─────────────────────────────────────────────
        if self.web:
            self.web.urlChanged.connect(self._on_url_changed)
            self.web.titleChanged.connect(self._on_title_changed)
            self.web.loadStarted.connect(self._on_load_started)
            self.web.loadProgress.connect(self._on_load_progress)
            self.web.loadFinished.connect(self._on_load_finished)

        self._update_nav_buttons()

    # ---------------------------------------------------------------- Slots --
    def _go_back(self):
        if self.web: self.web.back()

    def _go_forward(self):
        if self.web: self.web.forward()

    def _reload(self):
        if self.web: self.web.reload()

    def _go_home(self):
        if self.web: self.web.setUrl(QUrl("https://www.google.com"))

    def _navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if "." in text and " " not in text and not text.startswith("http"):
            text = "https://" + text
        elif not text.startswith("http"):
            text = "https://www.google.com/search?q=" + text.replace(" ", "+")
        if self.web: self.web.setUrl(QUrl(text))

    def _on_url_changed(self, qurl: QUrl):
        self.url_bar.setText(qurl.toString())
        # Security indicator
        is_secure = qurl.scheme() == "https"
        self.lock_label.setText("🔒" if is_secure else "⚠️")
        self.lock_label.setStyleSheet(
            f"color: {'#a6e3a1' if is_secure else '#f38ba8'}; font-size: 14px; padding: 0 4px;"
        )
        self._update_nav_buttons()

    def _on_title_changed(self, title: str):
        self.page_label.setText(title[:60] + ("…" if len(title) > 60 else ""))

    def _on_load_started(self):
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_label.setText("Loading…")
        self.btn_reload.setText("✕")
        self.btn_reload.clicked.disconnect()
        self.btn_reload.clicked.connect(self.web.stop)

    def _on_load_progress(self, pct: int):
        self.progress_bar.setValue(pct)

    def _on_load_finished(self, ok: bool):
        self.progress_bar.hide()
        self.status_label.setText("Done" if ok else "Failed to load")
        self.btn_reload.setText("↻")
        self.btn_reload.clicked.disconnect()
        self.btn_reload.clicked.connect(self._reload)
        self._update_nav_buttons()

    def _update_nav_buttons(self):
        if self.web:
            self.btn_back.setEnabled(self.web.history().canGoBack())
            self.btn_forward.setEnabled(self.web.history().canGoForward())
        else:
            self.btn_back.setEnabled(False)
            self.btn_forward.setEnabled(False)
