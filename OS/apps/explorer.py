import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QListWidget, QListWidgetItem, QTableWidget, 
                             QTableWidgetItem, QSplitter, QHeaderView, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
import theme
from apps.fs import VirtualFS, VirtualFile

class SigeonExplorer(QWidget):
    # Signals
    open_file_requested = pyqtSignal(str, object)  # Emits file_name, file_object

    def __init__(self, desktop_parent=None):
        super().__init__()
        self.desktop = desktop_parent
        self.fs = VirtualFS()
        self.current_directory = ["Home"]
        
        self.init_ui()
        self.navigate_to(["Home"])

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 1. Navigation / Address Bar
        self.nav_bar = QWidget(self)
        self.nav_bar.setFixedHeight(40)
        self.nav_bar.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid rgba(0, 0, 0, 0.08);")
        
        self.nav_layout = QHBoxLayout(self.nav_bar)
        self.nav_layout.setContentsMargins(8, 0, 8, 0)
        self.nav_layout.setSpacing(6)
        
        # Back / Forward / Up / Refresh Buttons
        self.btn_back = QPushButton("←", self.nav_bar)
        self.btn_back.setFixedSize(28, 28)
        self.btn_back.setStyleSheet("background: transparent; border: none; border-radius: 4px; font-size: 14px; color: #555;")
        self.btn_back.clicked.connect(self.go_back)
        self.nav_layout.addWidget(self.btn_back)
        
        self.btn_forward = QPushButton("→", self.nav_bar)
        self.btn_forward.setFixedSize(28, 28)
        self.btn_forward.setStyleSheet("background: transparent; border: none; border-radius: 4px; font-size: 14px; color: #ccc;") # disabled look
        self.nav_layout.addWidget(self.btn_forward)
        
        self.btn_up = QPushButton("↑", self.nav_bar)
        self.btn_up.setFixedSize(28, 28)
        self.btn_up.setStyleSheet("background: transparent; border: none; border-radius: 4px; font-size: 14px; color: #555;")
        self.btn_up.clicked.connect(self.go_up)
        self.nav_layout.addWidget(self.btn_up)
        
        self.btn_refresh = QPushButton("↻", self.nav_bar)
        self.btn_refresh.setFixedSize(28, 28)
        self.btn_refresh.setStyleSheet("background: transparent; border: none; border-radius: 4px; font-size: 14px; color: #555;")
        self.btn_refresh.clicked.connect(self.refresh_view)
        self.nav_layout.addWidget(self.btn_refresh)
        
        # Address bar
        self.address_input = QLineEdit(self.nav_bar)
        self.address_input.setReadOnly(True)
        self.address_input.setStyleSheet("background-color: #f3f3f3; border: 1px solid #e0e0e0; border-radius: 4px; padding: 4px 8px; font-size: 11px; color: #555;")
        self.nav_layout.addWidget(self.address_input, stretch=1)
        
        # Search input
        self.search_input = QLineEdit(self.nav_bar)
        self.search_input.setPlaceholderText("Search Pigeon")
        self.search_input.setFixedWidth(160)
        self.search_input.setStyleSheet("background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
        self.search_input.textChanged.connect(self.perform_search)
        self.nav_layout.addWidget(self.search_input)
        
        self.layout.addWidget(self.nav_bar)
        
        # 2. Main Content Splitter (Sidebar + File View)
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: rgba(0, 0, 0, 0.05); width: 1px; }")
        
        # Left Sidebar widget
        self.sidebar = QWidget(self)
        self.sidebar.setObjectName("explorer_sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 8, 0, 8)
        self.sidebar_layout.setSpacing(6)
        
        # Sidebar list widget
        self.sidebar_list = QListWidget(self.sidebar)
        self.sidebar_list.setObjectName("explorer_sidebar_list")
        self.sidebar_list.itemClicked.connect(self.sidebar_clicked)
        
        # Populating Sidebar
        self.add_sidebar_header("Favorites")
        self.add_sidebar_item("  Home", "logo", ["Home"])
        self.add_sidebar_item("  Recent", "logo_white", ["Recent"])
        self.add_sidebar_item("  Desktop", "folder_desktop", ["Home", "Desktop"])
        self.add_sidebar_item("  Downloads", "folder_downloads", ["Home", "Downloads"])
        
        self.add_sidebar_header("Locations")
        import string
        if sys.platform == "win32":
            import ctypes
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    self.add_sidebar_item(f"  {letter}:\\", "wing_drive", [f"{letter}:\\"])
                bitmask >>= 1
        else:
            self.add_sidebar_item("  Root (/)", "wing_drive", ["/"])
            
        self.sidebar_layout.addWidget(self.sidebar_list)
        self.splitter.addWidget(self.sidebar)
        
        # Right File/Folder area
        self.right_panel = QWidget(self)
        self.right_panel.setStyleSheet("background-color: #ffffff;")
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(16, 12, 16, 12)
        self.right_layout.setSpacing(14)
        
        # Recent Files Area (Lower)
        self.recent_container = QWidget(self.right_panel)
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_layout.setSpacing(6)
        
        self.recent_title = QLabel("Recent files", self.recent_container)
        self.recent_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #1a1f26;")
        self.recent_layout.addWidget(self.recent_title)
        
        # Table of files
        self.recent_table = QTableWidget(self.recent_container)
        self.recent_table.setObjectName("explorer_recent_table")
        self.recent_table.setColumnCount(3)
        self.recent_table.setHorizontalHeaderLabels(["Name", "Location", "Date modified"])
        self.recent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.recent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recent_table.cellDoubleClicked.connect(self.file_double_clicked)
        
        self.recent_layout.addWidget(self.recent_table)
        self.right_layout.addWidget(self.recent_container, stretch=1)
        
        self.splitter.addWidget(self.right_panel)
        
        # Set sizes (sidebar: 180, right panel: rest)
        self.splitter.setSizes([180, 520])
        self.layout.addWidget(self.splitter)
        
        # 3. Footer Status Bar
        self.status_bar = QWidget(self)
        self.status_bar.setFixedHeight(24)
        self.status_bar.setStyleSheet("background-color: #f3f3f3; border-top: 1px solid rgba(0,0,0,0.06);")
        self.status_layout = QHBoxLayout(self.status_bar)
        self.status_layout.setContentsMargins(12, 0, 12, 0)
        
        self.status_label = QLabel("7 items", self.status_bar)
        self.status_label.setStyleSheet("color: #606f7b; font-size: 10px;")
        self.status_layout.addWidget(self.status_label)
        
        self.status_layout.addStretch()
        
        self.storage_label = QLabel("42.6 GB free of 256 GB", self.status_bar)
        self.storage_label.setStyleSheet("color: #606f7b; font-size: 10px;")
        self.status_layout.addWidget(self.storage_label)
        
        self.layout.addWidget(self.status_bar)

    def add_sidebar_header(self, title):
        item = QListWidgetItem(title)
        item.setFlags(Qt.ItemFlag.NoItemFlags) # make header unclickable
        item.setData(Qt.ItemDataRole.UserRole, "header")
        font = item.font()
        font.setBold(True)
        font.setPointSize(9)
        item.setFont(font)
        item.setForeground(theme.QBrush(theme.QColor(theme.TEXT_MUTED)))
        self.sidebar_list.addItem(item)

    def add_sidebar_item(self, text, icon_name, path_list):
        item = QListWidgetItem(text)
        item.setIcon(theme.IconFactory.get_icon(icon_name, 16))
        item.setData(Qt.ItemDataRole.UserRole, path_list)
        self.sidebar_list.addItem(item)

    # Sidebar click handler
    def sidebar_clicked(self, item):
        path_list = item.data(Qt.ItemDataRole.UserRole)
        if path_list == "header" or not path_list:
            return
        
        if path_list == ["Recent"]:
            self.show_recent_only()
        else:
            self.navigate_to(path_list)

    # Navigation Methods
    def navigate_to(self, path_list):
        if path_list == ["Recent"]:
            self.show_recent_only()
            return
            
        node = self.fs.get_node(path_list)
        if node is None:
            return
            
        self.current_directory = path_list
        self.search_input.clear()
        
        # Update Address bar
        path_str = "Pigeon > " + " > ".join(path_list) + " >"
        self.address_input.setText(path_str)
        
        # Refresh View
        self.refresh_view()
        
        # Update Back button state
        self.btn_back.setEnabled(len(path_list) > 1 or path_list != ["Home"])
        self.btn_back.setStyleSheet(
            "background: transparent; border: none; border-radius: 4px; font-size: 14px; color: " +
            ("#555;" if self.btn_back.isEnabled() else "#ccc;")
        )

    def go_back(self):
        if len(self.current_directory) > 1:
            self.navigate_to(self.current_directory[:-1])
        elif self.current_directory != ["Home"]:
            self.navigate_to(["Home"])

    def go_up(self):
        self.go_back()

    def refresh_view(self):
                # Retrieve current node and separate folders/files
        node = self.fs.get_node(self.current_directory)
        folders = []
        files = []
        if isinstance(node, dict):
            for name, child in node.items():
                if isinstance(child, dict):
                    folders.append(name)
                else:
                    files.append(child)
        # Sort folder names alphabetically
        folders.sort()
        # Sort files by name
        files.sort(key=lambda f: f.name if hasattr(f, 'name') else str(f))
            
        # Re-populate Files Table
        self.recent_table.setRowCount(0)
        
        # Adjust header based on context
        if self.current_directory == ["Home"] or self.current_directory == ["Recent"]:
            self.recent_title.setText("Recent files")
            self.recent_title.setVisible(True)
            self.recent_table.setHorizontalHeaderLabels(["Name", "Location", "Date modified"])
            items_to_show = self.fs.get_recent_files()
            for row, file_obj in enumerate(items_to_show):
                self.recent_table.insertRow(row)
                
                # Icon mapping
                ext_map = {"txt": "file_txt", "pdf": "file_pdf", "png": "file_png", "mp3": "file_mp3", "sgpj": "logo"}
                icon_name = ext_map.get(file_obj.file_type, "file_generic")
                
                item_name = QTableWidgetItem(file_obj.name)
                item_name.setIcon(theme.IconFactory.get_icon(icon_name, 20))
                item_name.setData(Qt.ItemDataRole.UserRole, file_obj)
                self.recent_table.setItem(row, 0, item_name)
                
                item_loc = QTableWidgetItem(file_obj.location)
                self.recent_table.setItem(row, 1, item_loc)
                
                item_date = QTableWidgetItem(file_obj.date)
                self.recent_table.setItem(row, 2, item_date)
        else:
            self.recent_title.setVisible(False)
            self.recent_table.setHorizontalHeaderLabels(["Name", "Type", "Date modified"])
            row_idx = 0
            
            # Add folders first
            for f in folders:
                self.recent_table.insertRow(row_idx)
                icon_map = {"Music": "folder_music", "Videos": "folder_videos", "Pictures": "folder_pictures", "Downloads": "folder_downloads", "Desktop": "folder_desktop", "Documents": "folder_documents", "Projects": "folder_projects"}
                icon_name = icon_map.get(f, "folder")
                
                item_name = QTableWidgetItem(f)
                item_name.setIcon(theme.IconFactory.get_icon(icon_name, 20))
                item_name.setData(Qt.ItemDataRole.UserRole, f"FOLDER:{f}")
                self.recent_table.setItem(row_idx, 0, item_name)
                self.recent_table.setItem(row_idx, 1, QTableWidgetItem("Folder"))
                self.recent_table.setItem(row_idx, 2, QTableWidgetItem(""))
                row_idx += 1
                
            # Add files
            for file_obj in files:
                self.recent_table.insertRow(row_idx)
                ext_map = {"txt": "file_txt", "pdf": "file_pdf", "png": "file_png", "mp3": "file_mp3", "sgpj": "logo"}
                icon_name = ext_map.get(file_obj.file_type, "file_generic")
                
                item_name = QTableWidgetItem(file_obj.name)
                item_name.setIcon(theme.IconFactory.get_icon(icon_name, 20))
                item_name.setData(Qt.ItemDataRole.UserRole, file_obj)
                self.recent_table.setItem(row_idx, 0, item_name)
                self.recent_table.setItem(row_idx, 1, QTableWidgetItem(file_obj.file_type.upper()))
                self.recent_table.setItem(row_idx, 2, QTableWidgetItem(file_obj.date))
                row_idx += 1
            
        # Update status
        item_count = len(folders) + len(files)
        self.status_label.setText(f"{item_count} items")

    def show_recent_only(self):
        self.current_directory = ["Recent"]
        self.address_input.setText("Pigeon > Recent Files")
        self.folders_container.setVisible(False)
        self.recent_title.setText("Recent files")
        self.recent_title.setVisible(True)
        
        self.recent_table.setRowCount(0)
        recent_files = self.fs.get_recent_files()
        
        for row, file_obj in enumerate(recent_files):
            self.recent_table.insertRow(row)
            ext_map = {
                "txt": "file_txt",
                "pdf": "file_pdf",
                "png": "file_png",
                "mp3": "file_mp3",
                "sgpj": "logo",
            }
            icon_name = ext_map.get(file_obj.file_type, "file_generic")
            
            item_name = QTableWidgetItem(file_obj.name)
            item_name.setIcon(theme.IconFactory.get_icon(icon_name, 20))
            item_name.setData(Qt.ItemDataRole.UserRole, file_obj)
            self.recent_table.setItem(row, 0, item_name)
            
            item_loc = QTableWidgetItem(file_obj.location)
            self.recent_table.setItem(row, 1, item_loc)
            
            item_date = QTableWidgetItem(file_obj.date)
            self.recent_table.setItem(row, 2, item_date)
            
        self.status_label.setText(f"{len(recent_files)} items")

    # Double click table row handler
    def file_double_clicked(self, row, column):
        item = self.recent_table.item(row, 0)
        if item:
            file_obj = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(file_obj, VirtualFile):
                self.open_file_requested.emit(file_obj.name, file_obj)
            elif isinstance(file_obj, str) and file_obj.startswith("FOLDER:"):
                folder_name = file_obj.split(":", 1)[1]
                self.navigate_to(self.current_directory + [folder_name])

    # Search filter
    def perform_search(self, text):
        if not text:
            self.refresh_view()
            return
            
        # Simple local search
        node = self.fs.get_node(self.current_directory)
        if not isinstance(node, dict):
            return
            
        # Hide folders for search results
        self.folders_container.setVisible(False)
        self.recent_table.setRowCount(0)
        
        row = 0
        for name, child in node.items():
            if text.lower() in name.lower() and isinstance(child, VirtualFile):
                self.recent_table.insertRow(row)
                ext_map = {"txt": "file_txt", "pdf": "file_pdf", "png": "file_png", "mp3": "file_mp3", "sgpj": "logo"}
                icon_name = ext_map.get(child.file_type, "file_generic")
                
                item_name = QTableWidgetItem(child.name)
                item_name.setIcon(theme.IconFactory.get_icon(icon_name, 20))
                item_name.setData(Qt.ItemDataRole.UserRole, child)
                self.recent_table.setItem(row, 0, item_name)
                
                item_loc = QTableWidgetItem(child.file_type.upper())
                self.recent_table.setItem(row, 1, item_loc)
                
                item_date = QTableWidgetItem(child.date)
                self.recent_table.setItem(row, 2, item_date)
                row += 1
                
        self.status_label.setText(f"{row} search results")
