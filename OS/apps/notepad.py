import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
                             QPushButton, QMessageBox, QDialog, QLineEdit, QComboBox,
                             QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
import theme
from apps.fs import VirtualFS, VirtualFile


class SigeonSaveDialog(QDialog):
    """Custom in-OS 'Save As' dialog styled to match SigeonOS."""

    def __init__(self, fs, parent=None):
        super().__init__(parent)
        self.fs = fs
        self.result_filename = None
        self.result_folder = None

        self.setWindowTitle("Save Note")
        self.setFixedSize(360, 220)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(240, 244, 250, 0.98);
                border: 1px solid rgba(0, 0, 0, 0.12);
                border-radius: 12px;
            }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(12)

        # Title bar
        header = QHBoxLayout()
        header.setSpacing(8)
        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(theme.IconFactory.get_icon("notepad", 20).pixmap(20, 20))
        header.addWidget(icon_lbl)
        title = QLabel("Save Note As", self)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1a1f26;")
        header.addWidget(title)
        header.addStretch()
        lay.addLayout(header)

        # Separator
        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(0,0,0,0.06); border: none; max-height: 1px;")
        lay.addWidget(sep)

        # Form grid
        form = QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(10)

        # Filename
        name_lbl = QLabel("File name:", self)
        name_lbl.setStyleSheet("font-size: 11px; color: #2c3e50; font-weight: 600;")
        form.addWidget(name_lbl, 0, 0)

        self.name_input = QLineEdit(self)
        self.name_input.setText("MyNote.txt")
        self.name_input.selectAll()
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #d0d5dd;
                border-radius: 5px;
                padding: 5px 8px;
                font-size: 12px;
                color: #1a1f26;
            }
            QLineEdit:focus {
                border: 1px solid #0f82df;
            }
        """)
        form.addWidget(self.name_input, 0, 1)

        # Save location
        loc_lbl = QLabel("Save to:", self)
        loc_lbl.setStyleSheet("font-size: 11px; color: #2c3e50; font-weight: 600;")
        form.addWidget(loc_lbl, 1, 0)

        self.loc_combo = QComboBox(self)
        self.loc_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #d0d5dd;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 12px;
                color: #1a1f26;
            }
            QComboBox:focus {
                border: 1px solid #0f82df;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #d0d5dd;
                selection-background-color: rgba(15, 130, 223, 0.15);
                selection-color: #0f82df;
            }
        """)

        # Populate with folders from FS
        folders = [
            ("Desktop", ["Home", "Desktop"]),
            ("Documents", ["Home", "Documents"]),
            ("Downloads", ["Home", "Downloads"]),
            ("Projects", ["Home", "Projects"]),
        ]
        for name, path in folders:
            self.loc_combo.addItem(theme.IconFactory.get_icon("folder", 16), name, path)

        form.addWidget(self.loc_combo, 1, 1)
        lay.addLayout(form)

        lay.addStretch()

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.setFixedWidth(80)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #d0d5dd;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #f2f4f6;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Save", self)
        self.btn_save.setFixedWidth(80)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f82df;
                border: none;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3fa5fc;
            }
        """)
        self.btn_save.clicked.connect(self.accept_save)
        btn_row.addWidget(self.btn_save)

        lay.addLayout(btn_row)

        # Enter key shortcut
        self.name_input.returnPressed.connect(self.accept_save)

    def accept_save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setStyleSheet("""
                QLineEdit {
                    background-color: #fff5f5;
                    border: 1px solid #e74c3c;
                    border-radius: 5px;
                    padding: 5px 8px;
                    font-size: 12px;
                    color: #1a1f26;
                }
            """)
            return
        if "." not in name:
            name += ".txt"
        self.result_filename = name
        self.result_folder = self.loc_combo.currentData()
        self.accept()


class SigeonNotepad(QWidget):
    def __init__(self, filename=None, file_obj=None, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.fs = VirtualFS()
        self.filename = filename
        self.file_obj = file_obj
        self.save_folder = None  # Remembers where we last saved

        self.init_ui()
        if self.file_obj:
            self.load_file(self.file_obj)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Toolbar
        self.toolbar = QWidget(self)
        self.toolbar.setFixedHeight(34)
        self.toolbar.setStyleSheet("background-color: #f1f2f6; border-bottom: 1px solid rgba(0,0,0,0.06);")

        self.tb_layout = QHBoxLayout(self.toolbar)
        self.tb_layout.setContentsMargins(8, 0, 8, 0)
        self.tb_layout.setSpacing(6)

        # Status/Filename Label
        self.title_lbl = QLabel("New Note.txt", self.toolbar)
        self.title_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #57606f;")
        self.tb_layout.addWidget(self.title_lbl)

        self.tb_layout.addStretch()

        # New File Button
        self.btn_new = QPushButton("New Note", self.toolbar)
        self.btn_new.setStyleSheet("background-color: transparent; border: none; border-radius: 4px; padding: 4px 8px; font-size: 11px; color: #2f3542;")
        self.btn_new.clicked.connect(self.new_file)
        self.tb_layout.addWidget(self.btn_new)

        # Save Button
        self.btn_save = QPushButton("Save", self.toolbar)
        self.btn_save.setStyleSheet("background-color: #0f82df; border: none; border-radius: 4px; padding: 4px 10px; font-size: 11px; color: white; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_file)
        self.tb_layout.addWidget(self.btn_save)

        self.layout.addWidget(self.toolbar)

        # Text Editor area
        self.editor = QTextEdit(self)
        self.editor.setObjectName("notepad_editor")
        self.editor.setPlaceholderText("Write your notes here... Coo!")
        self.layout.addWidget(self.editor)

        # Styling
        self.setStyleSheet(theme.get_stylesheet())

    def load_file(self, file_obj):
        self.file_obj = file_obj
        self.filename = file_obj.name
        self.save_folder = None  # Will use file_obj.location to derive path
        self.title_lbl.setText(file_obj.name)
        self.editor.setPlainText(file_obj.content)

    def new_file(self):
        self.file_obj = None
        self.filename = None
        self.save_folder = None
        self.title_lbl.setText("New Note.txt")
        self.editor.clear()

    def save_file(self):
        content = self.editor.toPlainText()

        if not self.filename:
            # Show custom SigeonOS save dialog
            dialog = SigeonSaveDialog(self.fs, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.filename = dialog.result_filename
                self.save_folder = dialog.result_folder
            else:
                return  # User cancelled

        # Determine destination folder
        if self.save_folder:
            dest_folder = self.save_folder
        elif self.file_obj and self.file_obj.location:
            # Try to map location string back to path
            loc_map = {
                "Desktop": ["Home", "Desktop"],
                "Documents": ["Home", "Documents"],
                "Downloads": ["Home", "Downloads"],
                "Projects": ["Home", "Projects"],
                "Pictures": ["Home", "Pictures"],
                "Music": ["Home", "Music"],
            }
            dest_folder = loc_map.get(self.file_obj.location, ["Home", "Desktop"])
        else:
            dest_folder = ["Home", "Desktop"]

        success = self.fs.write_file(dest_folder, self.filename, content, "txt")
        if success:
            # Retrieve node to update our local reference
            node = self.fs.get_node(dest_folder)
            self.file_obj = node[self.filename]
            self.save_folder = dest_folder
            self.title_lbl.setText(self.filename)

            # Notify desktop to refresh explorer if it is open
            if self.desktop:
                self.desktop.refresh_explorers()

            # Briefly show success state on save button
            self.btn_save.setText("Saved!")
            self.btn_save.setStyleSheet("background-color: #2ec27e; border: none; border-radius: 4px; padding: 4px 10px; font-size: 11px; color: white; font-weight: bold;")
            QTimer.singleShot(1500, self.restore_save_btn)
        else:
            QMessageBox.critical(self, "Error", "Could not save the file to the virtual filesystem.")

    def restore_save_btn(self):
        self.btn_save.setText("Save")
        self.btn_save.setStyleSheet("background-color: #0f82df; border: none; border-radius: 4px; padding: 4px 10px; font-size: 11px; color: white; font-weight: bold;")
