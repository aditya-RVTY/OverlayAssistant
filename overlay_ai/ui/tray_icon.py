from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
import sys
# Note: User needs an icon.png, we will use a placeholder or create one if missing.

class SystemTray(QSystemTrayIcon):
    toggle_requested = Signal()
    clear_data_requested = Signal()

    def __init__(self, app):
        super().__init__(app)
        # For now, we rely on a default system icon if specific one fails
        # or we could generate a pixel map.
        self.setIcon(QIcon.fromTheme("applications-system")) 
        self.setVisible(True)
        self.setToolTip("Overlay AI Assistant")

        # Menu
        self.menu = QMenu()
        self.toggle_action = self.menu.addAction("Toggle Overlay")
        self.toggle_action.triggered.connect(self.toggle_requested.emit)
        
        self.clear_action = self.menu.addAction("Clear Data")
        self.clear_action.triggered.connect(self.clear_data_requested.emit)
        
        self.quit_action = self.menu.addAction("Quit")
        self.quit_action.triggered.connect(app.quit)
        
        self.setContextMenu(self.menu)
        
        # Click handler
        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_requested.emit()
