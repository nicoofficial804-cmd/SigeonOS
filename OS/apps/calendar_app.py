import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCalendarWidget, QLabel, QFrame
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import theme

class SigeonCalendarApp(QWidget):
    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # Left: Calendar Widget
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.selectionChanged.connect(self.date_changed)
        self.main_layout.addWidget(self.calendar, stretch=2)

        # Right: Details panel
        self.details_panel = QFrame(self)
        self.details_panel.setObjectName("settings_card")
        self.details_lay = QVBoxLayout(self.details_panel)
        self.details_lay.setContentsMargins(15, 15, 15, 15)
        self.details_lay.setSpacing(10)

        self.lbl_day_name = QLabel("", self.details_panel)
        self.lbl_day_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f82df;")
        self.details_lay.addWidget(self.lbl_day_name)

        self.lbl_day_num = QLabel("", self.details_panel)
        self.lbl_day_num.setStyleSheet("font-size: 48px; font-weight: bold;")
        self.details_lay.addWidget(self.lbl_day_num)

        self.lbl_month_year = QLabel("", self.details_panel)
        self.lbl_month_year.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.details_lay.addWidget(self.lbl_month_year)

        sep = QFrame(self.details_panel)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        self.details_lay.addWidget(sep)

        event_header = QLabel("Pigeon Flight Plan", self.details_panel)
        event_header.setStyleSheet("font-size: 11px; font-weight: bold;")
        self.details_lay.addWidget(event_header)

        self.event_desc = QLabel("", self.details_panel)
        self.event_desc.setWordWrap(True)
        self.event_desc.setStyleSheet("font-size: 10px;")
        self.details_lay.addWidget(self.event_desc)

        self.details_lay.addStretch()
        self.main_layout.addWidget(self.details_panel, stretch=1)

        self.date_changed()

    def date_changed(self):
        date = self.calendar.selectedDate()
        self.lbl_day_name.setText(date.toString("dddd").upper())
        self.lbl_day_num.setText(date.toString("dd"))
        self.lbl_month_year.setText(date.toString("MMMM yyyy"))
        day_of_week = date.dayOfWeek()
        if day_of_week == 1:
            self.event_desc.setText("Coop Meeting at 09:00. Weekly grain distribution review.")
        elif day_of_week == 3:
            self.event_desc.setText("Mid-week feather preening session. Cooing diagnostics optimal.")
        elif day_of_week == 5:
            self.event_desc.setText("Weekend migration flight path pre-check. Seed storage at 100%.")
        elif day_of_week in (6, 7):
            self.event_desc.setText("Coop rest day. Free flight allowed over local parks. \U0001f333")
        else:
            self.event_desc.setText("No migrations scheduled for today. Fly safe! \U0001f54a\ufe0f")
