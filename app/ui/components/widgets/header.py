from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget

from app.ui.styles import StyleSheet, DarkPalette

class HeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(StyleSheet.HEADER_WIDGET)
        self.setFixedHeight(120)
        
        layout: QVBoxLayout = QVBoxLayout(self)
        
        title: QLabel = QLabel("⬢ MORDOR v1.0")
        title.setStyleSheet(f"""
            font-size: 28pt;
            font-weight: 600;
            color: {DarkPalette.TEXT_PRIMARY.name()};
        """)

        layout.addWidget(title)


