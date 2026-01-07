
# Color Palette
COLORS = {
    "background": "rgba(30, 30, 40, 0.7)",
    "input_bg": "rgba(50, 50, 60, 0.6)",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0B0B0",
    "accent": "#7C4DFF",  # Deep Purple
    "accent_hover": "#651FFF",
    "user_msg_bg": "rgba(124, 77, 255, 0.8)",
    "ai_msg_bg": "rgba(60, 60, 70, 0.6)",
    "border": "rgba(255, 255, 255, 0.1)",
    "header_bg": "rgba(20, 20, 30, 0.8)"
}

STYLESHEET = f"""
QWidget {{
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    color: {COLORS['text_primary']};
}}

/* Main Chat Container */
#ChatContainer {{
    background-color: {COLORS['background']};
    border-radius: 12px;
    border: 1px solid {COLORS['border']};
}}

/* Chat Area (Scroll Area) */
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

/* Input Field */
/* Input Field */
QLineEdit, QTextEdit {{
    background-color: rgba(40, 40, 50, 0.95);
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px;
    color: {COLORS['text_primary']};
    font-size: 14px;
}}
QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {COLORS['accent']};
}}

/* Send Button */
QPushButton#SendButton {{
    background-color: {COLORS['accent']};
    border-radius: 8px;
    color: white;
    font-weight: bold;
    padding: 6px 12px;
}}
QPushButton#SendButton:hover {{
    background-color: {COLORS['accent_hover']};
}}

/* Scrollbar */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px 0px 0px 0px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    min-height: 20px;
    border-radius: 4px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}


#Header {{
    background-color: {COLORS['header_bg']};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}}

QPushButton#HeaderButton {{
    background: transparent;
    border: none;
    color: {COLORS['text_secondary']};
    font-weight: bold;
    font-size: 16px;
}}
QPushButton#HeaderButton:hover {{
    color: {COLORS['text_primary']};
}}
"""
