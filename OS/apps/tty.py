import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QProcess

class SigeonTTY(QWidget):
    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.init_ui()
        self.process.start("powershell.exe")

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.history = QTextEdit(self)
        self.history.setReadOnly(True)
        self.history.setStyleSheet("background-color: #1a1a1a; color: #e0e0e0; font-family: Consolas; font-size: 12px; border: none;")
        self.layout.addWidget(self.history)
        
        prompt_row = QWidget(self)
        prompt_row.setStyleSheet("background-color: #1a1a1a; border-top: 1px solid #2e2e2e;")
        row_lay = QHBoxLayout(prompt_row)
        row_lay.setContentsMargins(8, 2, 8, 2)
        
        self.prompt_lbl = QLabel("HOST TTY >", prompt_row)
        self.prompt_lbl.setStyleSheet("color: #ff9f43; font-family: Consolas; font-size: 12px; font-weight: bold;")
        row_lay.addWidget(self.prompt_lbl)
        
        self.cmd_input = QLineEdit(prompt_row)
        self.cmd_input.setStyleSheet("background-color: #1a1a1a; color: #ff9f43; font-family: Consolas; font-size: 12px; border: none;")
        self.cmd_input.returnPressed.connect(self.process_command)
        row_lay.addWidget(self.cmd_input, stretch=1)
        
        self.layout.addWidget(prompt_row)
        self.cmd_input.setFocus()
        
    def write_text(self, text, color="#e0e0e0"):
        # Very simple formatting
        html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>").replace(" ", "&nbsp;")
        self.history.append(f"<span style='color: {color};'>{html}</span>")
        scrollbar = self.history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.write_text(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.write_text(data, "#ff4a4a")

    def process_command(self):
        cmd = self.cmd_input.text()
        self.cmd_input.clear()
        if not cmd:
            return
            
        self.write_text(f"HOST TTY > {cmd}", "#ff9f43")
        self.process.write((cmd + "\n").encode('utf-8'))
