from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSizeGrip
)
from PySide6.QtCore import Qt, QPoint, QSize
from overlay_ai.ui.styles import STYLESHEET

class DraggableHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Header")
        self.setFixedHeight(40)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        
        self.title = QLabel("Overlay AI")
        self.title.setStyleSheet("font-weight: bold; color: white;")
        
        self.collapse_btn = QPushButton("-")
        self.collapse_btn.setObjectName("HeaderButton")
        self.collapse_btn.setFixedWidth(30)
        
        self.close_btn = QPushButton("×") 
        self.close_btn.setObjectName("HeaderButton")
        self.close_btn.setFixedWidth(30)
        
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.collapse_btn)
        self.layout.addWidget(self.close_btn)
        
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.resize(400, 600)
        self.setStyleSheet(STYLESHEET)
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("ChatContainer")
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        self.header = DraggableHeader(self)
        self.header.close_btn.clicked.connect(self.hide)
        self.header.collapse_btn.clicked.connect(self.toggle_collapse)
        self.layout.addWidget(self.header)
        
        # Content Container (for collapsing)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.content_container)
        
        # Size Grip
        self.sizegrip = QSizeGrip(self.central_widget)
        # Position logic for sizegrip usually requires resizeEvent override, 
        # but inside a layout it might be tricky. Let's add it to bottom right.
        # Ideally, QSizeGrip works best in corner. 
        # We can add a footer layout for it if needed, or overlay it.
        # But QMainWindow has specific flags. For now, let's just allow resizing via edges?
        # Frameless windows don't have native edges.
        # We'll stick to a simple grip at bottom right.
        self.sizegrip.setFixedSize(20, 20)
        self.sizegrip.setStyleSheet("background: transparent;")
        
        self.is_collapsed = False
        self.expanded_height = 600

    def add_content(self, widget):
        self.content_layout.addWidget(widget)

    def toggle_collapse(self):
        if self.is_collapsed:
            self.resize(self.width(), self.expanded_height)
            self.content_container.setVisible(True)
            self.header.collapse_btn.setText("-")
            self.is_collapsed = False
        else:
            self.expanded_height = self.height()
            self.content_container.setVisible(False)
            self.resize(self.width(), self.header.height())
            self.header.collapse_btn.setText("+")
            self.is_collapsed = True

    def resizeEvent(self, event):
        # Move sizegrip to bottom right
        rect = self.rect()
        self.sizegrip.move(rect.right() - self.sizegrip.width(), rect.bottom() - self.sizegrip.height())
        super().resizeEvent(event)

