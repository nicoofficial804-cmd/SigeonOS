import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
import theme

class SigeonWeather(QWidget):
    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        
        # Weather Header
        self.header_card = QFrame(self)
        self.header_card.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #72c6ff, stop:1 #0073cc); border-radius: 8px; padding: 12px; border: none;")
        self.header_lay = QHBoxLayout(self.header_card)
        
        # Weather Text
        text_lay = QVBoxLayout()
        text_lay.setSpacing(2)
        self.loc_lbl = QLabel("SkyNest Base", self.header_card)
        self.loc_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.temp_lbl = QLabel("22°C", self.header_card)
        self.temp_lbl.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")
        self.cond_lbl = QLabel("Sunny & Calm • Cooing Index: HIGH", self.header_card)
        self.cond_lbl.setStyleSheet("font-size: 11px; color: #eef4fc; font-weight: 500;")
        text_lay.addWidget(self.loc_lbl)
        text_lay.addWidget(self.temp_lbl)
        text_lay.addWidget(self.cond_lbl)
        self.header_lay.addLayout(text_lay)
        
        self.header_lay.addStretch()
        
        # Visual Icon
        self.icon_lbl = QLabel(self.header_card)
        self.icon_lbl.setPixmap(theme.IconFactory.get_icon("weather", 64).pixmap(64, 64))
        self.header_lay.addWidget(self.icon_lbl)
        
        self.layout.addWidget(self.header_card)
        
        # Diagnostics/Stats grid
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(10)
        
        self.add_stat_card("Wind", "NNE 8 kts", "Optimal Flight Pattern")
        self.add_stat_card("Humidity", "54%", "Dry Feathers")
        self.add_stat_card("Visibility", "15 miles", "Clear Sight")
        
        self.layout.addLayout(self.stats_row)
        
        # Weekly Forecast title
        self.forecast_title = QLabel("Weekly Flight Forecast", self)
        self.forecast_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50; margin-top: 5px;")
        self.layout.addWidget(self.forecast_title)
        
        # Weekly Forecast Row
        self.forecast_row = QHBoxLayout()
        self.forecast_row.setSpacing(6)
        
        forecasts = [
            ("Mon", "21°C", "weather", "Clear"),
            ("Tue", "22°C", "weather", "Clear"),
            ("Wed", "18°C", "cloud_nest", "Drizzle"),
            ("Thu", "19°C", "weather", "Cloudy"),
            ("Fri", "23°C", "weather", "Peak Coo")
        ]
        
        for day, temp, icon, state in forecasts:
            card = QFrame()
            card.setObjectName("settings_card")
            lay = QVBoxLayout(card)
            lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.setSpacing(2)
            
            day_lbl = QLabel(day, card)
            day_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #7f8c8d;")
            ico_lbl = QLabel(card)
            ico_lbl.setPixmap(theme.IconFactory.get_icon(icon, 24).pixmap(24, 24))
            temp_lbl = QLabel(temp, card)
            temp_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #1a1f26;")
            state_lbl = QLabel(state, card)
            state_lbl.setStyleSheet("font-size: 8px; color: #95a5a6;")
            
            lay.addWidget(day_lbl, 0, Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(ico_lbl, 0, Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(temp_lbl, 0, Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(state_lbl, 0, Qt.AlignmentFlag.AlignCenter)
            
            self.forecast_row.addWidget(card)
            
        self.layout.addLayout(self.forecast_row)

    def add_stat_card(self, title, val, desc):
        card = QFrame(self)
        card.setObjectName("settings_card")
        lay = QVBoxLayout(card)
        lay.setSpacing(1)
        
        title_lbl = QLabel(title, card)
        title_lbl.setStyleSheet("font-size: 9px; color: #7f8c8d;")
        val_lbl = QLabel(val, card)
        val_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        desc_lbl = QLabel(desc, card)
        desc_lbl.setStyleSheet("font-size: 8px; color: #95a5a6;")
        
        lay.addWidget(title_lbl)
        lay.addWidget(val_lbl)
        lay.addWidget(desc_lbl)
        
        self.stats_row.addWidget(card)
