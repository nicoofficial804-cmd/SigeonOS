import sys
import datetime
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel
from PyQt6.QtCore import Qt
from apps.fs import VirtualFS, VirtualFile

PIGEON_ASCII = """
      .-.
     (o.o)   Proprietary Terminal
      |=|    --------------------
     /   \\   OS: SigeonOS 10.0.0
    //     \\\\ Kernel: PigeonCore-1.2
   //       \\ Shell: prop_sh 1.0
  ((         )) RAM: 16.0 GB
   \\       //  Pigeon ID: SP-2024
    '-...-'
"""

# Removed Pigeon Facts

MATRIX_LINES = [
    "01001100 01001001 01001110 01010101 01011000",
    "10100101 SYSTEM BOOT OK... COOING INSTALLED",
    "COONEST: ESTABLISHING COOP CONNECTION...",
    "SECURE ROUTE: NEST_GATEWAY [192.168.1.100]",
    "DECRYPTION KEY: BREADCRUMBS_SECRET_2026",
    "PIGEON_CORE: OVERCLOCKING TO 3.70 GHz",
    "WARNING: SEED INTAKE OPTIMAL",
    "THE MATRIX FEEDS THE FLOCK..."
]

class SigeonTerminal(QWidget):
    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.fs = VirtualFS()
        self.current_path = ["Home"]
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Text history
        self.history = QTextEdit(self)
        self.history.setObjectName("terminal_history")
        self.history.setReadOnly(True)
        self.history.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.layout.addWidget(self.history)
        
        # Command line prompt row
        prompt_row = QWidget(self)
        prompt_row.setStyleSheet("background-color: #1a1a1a; border-top: 1px solid #2e2e2e;")
        row_lay = QHBoxLayout(prompt_row)
        row_lay.setContentsMargins(8, 2, 8, 2)
        row_lay.setSpacing(4)
        
        self.prompt_lbl = QLabel(f"[{'/'.join(self.current_path)}]$ ", prompt_row)
        self.prompt_lbl.setStyleSheet("color: #0f82df; font-family: 'Consolas', monospace; font-size: 12px; font-weight: bold;")
        row_lay.addWidget(self.prompt_lbl)
        
        self.cmd_input = QLineEdit(prompt_row)
        self.cmd_input.setObjectName("terminal_input")
        self.cmd_input.returnPressed.connect(self.process_command)
        row_lay.addWidget(self.cmd_input, stretch=1)
        
        self.layout.addWidget(prompt_row)
        
        # Styling
        self.setStyleSheet("""
            QTextEdit#terminal_history {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: none;
            }
            QLineEdit#terminal_input {
                background-color: #1a1a1a;
                color: #4af626;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: none;
            }
        """)
        
        # Welcome message
        self.write_line("Welcome to Proprietary Terminal [prop_sh v1.0].")
        self.write_line("Type 'help' to see available commands.\n")
        
        # Give focus to input
        self.cmd_input.setFocus()

    def write_line(self, text, color="#e0e0e0"):
        self.history.append(f"<span style='color: {color};'>{text.replace(chr(10), '<br>') }</span>")
        scrollbar = self.history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def process_command(self):
        raw_cmd = self.cmd_input.text().strip()
        self.cmd_input.clear()
        
        if not raw_cmd:
            return
            
        # Log command in history
        self.write_line(f"[{'/'.join(self.current_path)}]$ {raw_cmd}", "#0f82df")
        
        parts = raw_cmd.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Execute command
        if cmd == "help":
            self.cmd_help()
        elif cmd in ("dir", "ls"):
            self.cmd_ls()
        elif cmd == "cd":
            self.cmd_cd(args)
        elif cmd == "neofetch" or cmd == "pigeonfetch":
            self.cmd_neofetch()
        elif cmd == "cat":
            self.cmd_cat(args)
        elif cmd == "echo":
            self.write_line(" ".join(args))
        elif cmd == "clear":
            self.history.clear()
        elif cmd == "date":
            self.write_line(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        elif cmd == "matrix":
            self.cmd_matrix()
        elif cmd == "exit":
            if self.parent() and hasattr(self.parent(), "close_window"):
                self.parent().close_window()
        else:
            self.write_line(f"prop_sh: command not found: {cmd}. Type 'help' for support.", "#ff4a4a")
            
        self.write_line("") # Empty separator line

    def cmd_help(self):
        self.write_line("Available SigeonOS commands:")
        self.write_line("  help         Show this list of commands")
        self.write_line("  ls / dir     List files in current directory")
        self.write_line("  cd <dir>     Change directory")
        self.write_line("  cat <file>   Print the content of a file")
        self.write_line("  neofetch     Show system specifications and art")
        self.write_line("  matrix       Trigger digital code sequence")
        self.write_line("  date         Show current system date and time")
        self.write_line("  echo <text>  Print text to console")
        self.write_line("  clear        Clear the screen")
        self.write_line("  exit         Close the terminal")

    def cmd_cd(self, args):
        if not args:
            self.current_path = ["Home"]
            self.update_prompt()
            return
            
        target = args[0]
        if target == "..":
            if len(self.current_path) > 1:
                self.current_path.pop()
            elif self.current_path != ["Home"]:
                self.current_path = ["Home"]
            self.update_prompt()
            return
            
        new_path = list(self.current_path)
        new_path.append(target)
        node = self.fs.get_node(new_path)
        if isinstance(node, dict):
            self.current_path = new_path
            self.update_prompt()
        else:
            self.write_line(f"cd: {target}: No such directory", "#ff4a4a")
            
    def update_prompt(self):
        self.prompt_lbl.setText(f"[{'/'.join(self.current_path)}]$ ")

    def cmd_ls(self):
        node = self.fs.get_node(self.current_path)
        
        if not isinstance(node, dict) or not node:
            self.write_line("(directory is empty)")
            return
            
        self.write_line(f"Listing directory: {'/'.join(self.current_path)}")
        for f, item in node.items():
            if isinstance(item, dict):
                # Directory
                self.write_line(f"  [DIR]  {f}", "#3fa5fc")
            else:
                # File
                self.write_line(f"  [FILE] {f} ({item.file_type.upper()})", "#2ec27e")

    def cmd_neofetch(self):
        self.write_line(PIGEON_ASCII, "#4af626")

    def cmd_cat(self, args):
        if not args:
            self.write_line("Usage: cat <filename>", "#ff4a4a")
            return
        filename = args[0]
        file_obj = self.fs.get_file(self.current_path, filename)
        
        if file_obj:
            self.write_line(file_obj.content, "#ffffff")
        else:
            self.write_line(f"cat: {filename}: File not found in current directory.", "#ff4a4a")

    def cmd_matrix(self):
        self.write_line("System diagnostics check override...", "#4af626")
        for line in MATRIX_LINES:
            self.write_line(line, "#2ecc71")
        self.write_line("Diagnostic check complete. Status: COOP HEATING OPTIMAL", "#4af626")
