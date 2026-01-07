import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QScrollArea, QLabel, QFrame, QFileDialog, QSizePolicy, QApplication
)
from PySide6.QtCore import Signal, Qt
from overlay_ai.ui.styles import COLORS
from overlay_ai.services.capture_service import capture_screen
from overlay_ai.ui.worker import AIWorker, IngestWorker

class AutoResizingTextEdit(QTextEdit):
    return_pressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setPlaceholderText("Ask about your screen...")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.textChanged.connect(self.adjust_height)
        self.setFixedHeight(40) # Initial height matches single line
        self.max_height = 100

    def adjust_height(self):
        doc_height = self.document().size().height()
        # Add some padding logic if needed, usually doc_height is enough
        new_height = int(doc_height + 10) 
        if new_height > self.max_height:
            new_height = self.max_height
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        if new_height < 40: new_height = 40
        self.setFixedHeight(new_height)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            self.return_pressed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

class ChatWidget(QWidget):
    message_sent = Signal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Chat History Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(10)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Input Area
        self.input_container = QWidget()
        self.input_layout = QHBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.upload_btn = QPushButton("+")
        self.upload_btn.setFixedWidth(30)
        self.upload_btn.setToolTip("Upload User Manual (PDF/TXT)")
        self.upload_btn.clicked.connect(self.upload_manual)
        
        self.input_field = AutoResizingTextEdit()
        self.input_field.return_pressed.connect(self.send_message)
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setObjectName("SendButton")
        self.send_btn.setFixedWidth(40)
        self.send_btn.clicked.connect(self.send_message)
        
        self.input_layout.addWidget(self.upload_btn)
        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.send_btn)

        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.input_container)
        
        self.worker = None
        self.ingest_worker = None
        self.history = []

    def upload_manual(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open User Manual", "", "Documents (*.pdf *.txt *.docx)")
        if fname:
            self.add_message(f"Uploading and processing {fname}...", is_user=False)
            self.ingest_worker = IngestWorker(fname)
            self.ingest_worker.finished.connect(self.on_ingest_finished)
            self.ingest_worker.start()

    def on_ingest_finished(self, result):
        self.add_message(result, is_user=False)
    
    def clear_history(self):
        self.history = []
        # Remove all items from layout
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.add_message("History cleared.", is_user=False)

    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if text:
            # 1. Update UI and History with User Message
            self.add_message(text, is_user=True)
            self.history.append({"role": "user", "content": text})
            
            # Limit history
            if len(self.history) > 10:
                self.history = self.history[-10:]

            self.message_sent.emit(text)
            self.input_field.clear()
            self.input_field.setDisabled(True)
            self.show_loading()
            
            # --- Smart Capture Logic ---
            # --- Smart Capture Logic ---
            # Strict triggers for "Explicitly Told"
            vision_keywords = [
                "@screen", "capture screen", "read screen", "check screen", 
                "analyze screen", "look at screen", "what is on my screen"
            ]
            should_capture = any(phrase in text.lower() for phrase in vision_keywords)
            

            
            image = None
            print("should_capture", should_capture)
            if should_capture:
                # Hide specific to capture
                main_window = self.window()
                main_window.hide()
                QApplication.processEvents()
                time.sleep(0.2)
                
                try:
                    image = capture_screen()
                except Exception as e:
                    print(f"Capture failed: {e}")
                
                main_window.show()
                main_window.activateWindow()
            # ---------------------------
            
            # Start Worker
            self.worker = AIWorker(text, self.history, image=image)
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()

    def on_worker_finished(self, response):
        # 2. Update UI and History with Assistant Response
        self.add_message(response, is_user=False)
        self.history.append({"role": "assistant", "content": response})
        
        self.input_field.setDisabled(False)
        self.input_field.setFocus()

    def add_message(self, text, is_user=False):
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Style logic
        bg_color = COLORS['user_msg_bg'] if is_user else COLORS['ai_msg_bg']
        align = Qt.AlignRight if is_user else Qt.AlignLeft
        
        bubble.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                line-height: 1.4;
            }}
        """)
        
        # Adjust size policy to ensure it grows vertically
        from PySide6.QtWidgets import QSizePolicy
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        # Limit maximum width to 80% of scroll area to look like a proper chat bubble
        # This helps with wrapping
        bubble.setMaximumWidth(int(self.scroll_area.width() * 0.8))

        # Container to handle alignment
        container = QWidget()
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(0, 5, 0, 5) # Add vertical spacing between bubbles
        c_layout.setAlignment(align)
        c_layout.addWidget(bubble)
        
        self.scroll_layout.addWidget(container)
        
        # Auto-scroll to bottom
        # Use simple timer to wait for layout update or process events
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def show_loading(self):
        # We could add a temporary widget/label here
        pass
