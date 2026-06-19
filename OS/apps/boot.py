import os
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
import theme
import animations

class SigeonBootScreen(QWidget):
    # Signal emitted when boot finishes (either video completes or error timeout expires)
    boot_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Full black background
        self.setStyleSheet("background-color: #000000;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Check if assets/boot.mp4 exists
        boot_video_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "boot.mp4")
        boot_audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "boot.mp3")
        
        if os.path.exists(boot_video_path):
            # 1. Video and audio play mode
            self.video_widget = QVideoWidget(self)
            self.layout.addWidget(self.video_widget)
            
            # Setup media player for video
            self.video_player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.video_player.setAudioOutput(self.audio_output)
            self.video_player.setVideoOutput(self.video_widget)
            
            self.video_player.setSource(QUrl.fromLocalFile(boot_video_path))
            
            # Setup audio player for boot.mp3 if exists
            self.audio_player = None
            if os.path.exists(boot_audio_path):
                self.audio_player = QMediaPlayer(self)
                self.sound_output = QAudioOutput(self)
                self.audio_player.setAudioOutput(self.sound_output)
                self.audio_player.setSource(QUrl.fromLocalFile(boot_audio_path))
            
            # Connect signals
            self.video_player.mediaStatusChanged.connect(self.on_media_status_changed)
            
            # Start playing when shown
            QTimer.singleShot(100, self.start_playback)
        else:
            # 2. Warning message mode (centered for 3 seconds)
            self.warning_label = QLabel(self)
            self.warning_label.setText(
                "⚠️ BOOT SCREEN NOT FOUND\n\n"
                "YOUR SIGEONOS MAY BE CORRUPTED"
            )
            self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.warning_label.setStyleSheet("""
                font-family: 'Courier New', monospace, 'Segoe UI';
                font-size: 16px;
                font-weight: bold;
                color: #ff3333;
                background-color: transparent;
                line-height: 1.6;
            """)
            self.layout.addWidget(self.warning_label)
            
            # Play a soft error tone or just wait 3 seconds
            # Wait 3 seconds then finish
            self.error_timer = QTimer(self)
            self.error_timer.setSingleShot(True)
            self.error_timer.timeout.connect(self.on_boot_timeout)
            self.error_timer.start(3000)

    def start_playback(self):
        try:
            self.video_player.play()
            if self.audio_player:
                self.audio_player.play()
        except Exception as e:
            print("Error playing boot media:", e)
            # Fallback to direct boot finish
            self.boot_finished.emit()

    def on_media_status_changed(self, status):
        # When media reaches the end, transition
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.boot_finished.emit()

    def on_boot_timeout(self):
        # Fade out warning message, then emit boot_finished
        animations.fade_out(self.warning_label, duration=500, callback=self.boot_finished.emit)
