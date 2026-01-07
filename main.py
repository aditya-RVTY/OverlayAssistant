import sys
import os
import threading
import keyboard
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import Signal, QObject, Slot

from overlay_ai.ui.overlay_window import OverlayWindow
from overlay_ai.ui.chat_widget import ChatWidget
from overlay_ai.ui.tray_icon import SystemTray

# Signal helper to handle hotkey from a different thread
class HotkeySignal(QObject):
    triggered = Signal()

def create_placeholder_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor("#7C4DFF"))
    return QIcon(pixmap)

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Create the window and widgets
    overlay = OverlayWindow()
    chat_widget = ChatWidget()
    overlay.add_content(chat_widget)
    
    # Create Tray
    tray = SystemTray(app)
    tray.setIcon(create_placeholder_icon())
    
    # Toggle Logic
    def toggle_overlay():
        if overlay.isVisible():
            overlay.hide()
        else:
            overlay.show()
            overlay.activateWindow()
            chat_widget.input_field.setFocus()

    tray.toggle_requested.connect(toggle_overlay)
    
    def clear_data():
        from overlay_ai.services.rag_service import rag_service
        msg = rag_service.clear_index()
        chat_widget.clear_history()
        chat_widget.add_message(f"Data Cleared: {msg}", is_user=False)
        
    tray.clear_data_requested.connect(clear_data)
    
    # Hotkey Logic
    hotkey_signal = HotkeySignal()
    hotkey_signal.triggered.connect(toggle_overlay)
    
    def on_hotkey():
        hotkey_signal.triggered.emit()

    try:
        keyboard.add_hotkey('ctrl+shift+a', on_hotkey)
    except ImportError:
        print("Keyboard library failed to set hotkey (permissions?)")

    # Cleanup on Exit
    def cleanup():
        print("Cleaning up...")
        try:
            keyboard.unhook_all()
        except:
            pass
            
    app.aboutToQuit.connect(cleanup)

    # Start Hidden? Or Show once to helpful?
    # Let's show it once so user knows it exists
    print("Starting Overlay...")
    overlay.show()
    
    exit_code = app.exec()
    print("Exiting...")
    os._exit(exit_code)

if __name__ == "__main__":
    main()
