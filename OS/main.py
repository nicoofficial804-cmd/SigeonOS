import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, QStackedWidget
from PyQt6.QtCore import Qt, QPoint, QEvent, QRect
from PyQt6.QtGui import QIcon, QMouseEvent
import theme
import animations

# Import components
from desktop import SigeonDesktop
from taskbar import SigeonTaskbar
from start_menu import SigeonStartMenu
from apps.login import SigeonLoginScreen
from apps.boot import SigeonBootScreen
from apps.setup import SigeonSetupScreen
from apps.users import has_users
from apps.fs import VirtualFS, VirtualFile

class SigeonMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SigeonOS Emulator")
        
        # Set window icon
        self.setWindowIcon(theme.IconFactory.get_icon("logo", 32))
        
        # Initialize virtual file system
        self.fs = VirtualFS()
        
        self.init_ui()
        self.installEventFilter(self) # For click-away start menu hide
        
        # --- MODIFICA PER VERO FULLSCREEN BORDERLESS ---
        # Rimuove le decorazioni della finestra a livello di Window Manager (niente bordi o barre del titolo)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        
        # Recupera la risoluzione reale dello schermo principale e forza le dimensioni geometriche
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
            
        # Attiva la modalità fullscreen nativa
        self.showFullScreen()
        # -----------------------------------------------
    
    def init_ui(self):
        # 1. Stacked Widget as Central Widget
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # 2. Page 0: Boot Screen
        self.boot_screen = SigeonBootScreen(self)
        self.boot_screen.boot_finished.connect(self.on_boot_finished)
        self.stacked_widget.addWidget(self.boot_screen)
        
        # 3. Page 1: Setup Screen (For first boot)
        self.setup_screen = SigeonSetupScreen(self)
        self.setup_screen.setup_completed.connect(self.on_setup_completed)
        self.stacked_widget.addWidget(self.setup_screen)
        
        # 4. Page 2: Login Screen
        self.login_screen = SigeonLoginScreen(self)
        self.login_screen.login_successful.connect(self.on_login_success)
        self.stacked_widget.addWidget(self.login_screen)
        
        # 5. Page 3: Desktop Workspace Area
        self.desktop_container = QWidget(self)
        self.desktop_layout = QVBoxLayout(self.desktop_container)
        self.desktop_layout.setContentsMargins(0, 0, 0, 0)
        self.desktop_layout.setSpacing(0)
        
        self.desktop = SigeonDesktop(self)
        self.desktop_layout.addWidget(self.desktop, stretch=1)
        
        # Taskbar (Bottom)
        self.taskbar = SigeonTaskbar(self)
        self.desktop_layout.addWidget(self.taskbar)
        
        # Start Menu (Floats above desktop, child of desktop_container for proper stacking)
        self.start_menu = QStartMenuWrapper(self.desktop_container, self)
        
        self.stacked_widget.addWidget(self.desktop_container)
        
        # Connect Signals
        self.taskbar.start_triggered.connect(self.toggle_start_menu)
        self.taskbar.app_triggered.connect(self.launch_app)
        self.start_menu.menu.app_launch_requested.connect(self.launch_app)
        self.start_menu.menu.file_open_requested.connect(self.handle_recommended_action)
        self.start_menu.menu.logout_requested.connect(self.on_logout_requested)
        
        # Show Boot Screen first
        self.stacked_widget.setCurrentIndex(0)
    
    def on_boot_finished(self):
        def proceed():
            if not has_users():
                # Switch to Setup Screen (Page 1)
                self.stacked_widget.setCurrentIndex(1)
            else:
                # Switch to Login Screen (Page 2)
                self.login_screen.reload_users()
                self.stacked_widget.setCurrentIndex(2)
                self.login_screen.start_appear_animation()
            
        animations.fade_out(self.boot_screen, duration=450, callback=proceed)
    
    def on_setup_completed(self, username):
        def show_login():
            self.login_screen.reload_users()
            self.stacked_widget.setCurrentIndex(2)
            self.login_screen.start_appear_animation()
            
        animations.fade_out(self.setup_screen, duration=450, callback=show_login)
    
    def on_login_success(self, username):
        self.fs.set_current_user(username)
        # Update username in Start Menu bottom bar
        self.start_menu.menu.prof_name.setText(username)
        
        # Reset desktop for this user
        self.desktop.load_desktop_icons()
        for app_id in list(self.desktop.open_windows.keys()):
            self.desktop.open_windows[app_id].close_window()
        
        def show_desktop():
            self.stacked_widget.setCurrentIndex(3)
            self.desktop.setFocus()
            animations.fade_in(self.desktop_container, duration=500)
            animations.fade_in(self.desktop_container, duration=500)
            
        animations.fade_out(self.login_screen, duration=450, callback=show_desktop)

    def on_logout_requested(self):
        self.hide_start_menu(animate=False)
        self.login_screen.reset()
        self.stacked_widget.setCurrentIndex(2)
        self.login_screen.start_appear_animation()
    
    def toggle_start_menu(self):
        if getattr(self, "start_menu_visible_target", False):
            self.hide_start_menu()
        else:
            self.show_start_menu()
    
    def show_start_menu(self):
        self.start_menu_visible_target = True
        if hasattr(self.start_menu, "_slide_anim") and self.start_menu._slide_anim is not None:
            try:
                self.start_menu._slide_anim.stop()
            except RuntimeError:
                pass
            
        x = 10
        y = self.height() - self.taskbar.height() - self.start_menu.height() - 10
        self.start_menu.move(x, y)
        self.start_menu.show()
        self.start_menu.raise_()
        animations.slide_in_from_bottom(self.start_menu, duration=250, offset=40)
        self.start_menu.menu.search_input.setFocus()
    
    def hide_start_menu(self, animate=True):
        self.start_menu_visible_target = False
        if hasattr(self.start_menu, "_slide_anim") and self.start_menu._slide_anim is not None:
            try:
                self.start_menu._slide_anim.stop()
            except RuntimeError:
                pass
            
        if animate:
            animations.slide_out_to_bottom(self.start_menu, duration=200, offset=40)
        else:
            self.start_menu.hide()
    
    def launch_app(self, app_id):
        # Launch app on desktop
        self.desktop.open_app(app_id)
        if getattr(self, "start_menu_visible_target", False):
            self.hide_start_menu(animate=False)
    
    def handle_recommended_action(self, action_id):
        if action_id == "welcome":
            QMessageBox.information(
                self, "Welcome to SigeonOS", 
                "Coo! Welcome to SigeonOS, a modern operating system built on pigeon flight logic.\n\n"
                "Features to explore:\n"
                "\u2022 Files: Manage documents, audio and flight plans\n"
                "\u2022 Terminal: Run 'neofetch' or 'pigeon-fact'\n"
                "\u2022 WingStore: Install the 'Flappy Pigeon' mini-game!"
            )
        elif action_id == "tips":
            QMessageBox.information(
                self, "Pigeon OS Tips", 
                "Cooing Tip #1:\nDouble-click text files inside File Explorer to edit them in Feather Notes.\n\n"
                "Cooing Tip #2:\nChange wallpapers under Settings \u003e Personalization."
            )
        elif action_id == "update":
            # Open Settings app and go to Updates tab
            self.launch_app("settings")
            win = self.desktop.open_windows.get("settings")
            if win:
                win.content_container.layout().itemAt(0).widget().menu_list.setCurrentRow(9)
        else:
            # It's a file, e.g. "Notes.txt" or "Flight_Plan.sgpj"
            # Look it up in virtual filesystem and open it
            # Pinned items paths:
            paths = {
                "Flight_Plan.sgpj": (["Home", "Projects"], "Flight_Plan.sgpj"),
                "Screenshot_2024-05-20.png": (["Home", "Pictures"], "Screenshot_2024-05-20.png"),
                "Notes.txt": (["Home", "Desktop"], "Notes.txt")
            }
            if action_id in paths:
                folder, fname = paths[action_id]
                file_obj = self.fs.get_file(folder, fname)
                if file_obj:
                    self.desktop.open_file(fname, file_obj)
    
    # Keyboard shortcut handling for Fullscreen toggle
    
    # Event filter to hide start menu when clicking outside of it
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if isinstance(event, QMouseEvent) and getattr(self, "start_menu_visible_target", False):
                click_pos = event.globalPosition().toPoint()
                menu_rect = self.start_menu.geometry()
                # Map menu rect to global coordinates
                menu_global_topleft = self.desktop_container.mapToGlobal(menu_rect.topLeft())
                menu_global_rect = QRect(menu_global_topleft, menu_rect.size())
                
                # Check if click is on the Start button specifically
                start_btn_rect = self.taskbar.btn_start.geometry()
                start_btn_global_topleft = self.taskbar.mapToGlobal(start_btn_rect.topLeft())
                start_btn_global_rect = QRect(start_btn_global_topleft, start_btn_rect.size())
                
                if not menu_global_rect.contains(click_pos) and not start_btn_global_rect.contains(click_pos):
                    self.hide_start_menu(animate=True)
                    
        return super().eventFilter(obj, event)

# Helper wrapper to make start menu overlay nice and clean
class QStartMenuWrapper(QWidget):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(340, 480)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.menu = SigeonStartMenu(self)
        self.layout.addWidget(self.menu)
        
        self.menu.show()
        self.hide() # Hidden initially

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app style
    app.setStyle("Fusion")
    
    window = SigeonMainWindow()
    window.show()
    sys.exit(app.exec())