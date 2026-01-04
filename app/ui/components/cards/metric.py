from PyQt6.QtWidgets import QFrame, QVBoxLayout, QGraphicsDropShadowEffect, QLabel
from PyQt6.QtGui import QColor

from typing import Any

from app.ui.styles import DarkPalette

class MetricCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str, color=None):
        super().__init__()
        self.accent_color: Any = color or DarkPalette.ACCENT_BLUE
        self.setFixedHeight(115)
        self.setMinimumWidth(190)
        
        self.shadow: QGraphicsDropShadowEffect = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)
        
        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(2)
        
        self.title_label: QLabel = QLabel(title.upper())
        self.title_label.setStyleSheet(
        f"""
            color: {DarkPalette.TEXT_MUTED.name()}; 
            font-size: 7.5pt; 
            font-weight: 700; 
            letter-spacing: 1px;
        """
        )
        
        self.value_label: QLabel = QLabel(value)
        self.value_label.setStyleSheet(
            f"""
            color: {DarkPalette.TEXT_PRIMARY.name()}; 
            font-size: 17pt; 
            font-weight: 800;
            """
        )
        
        self.sub_label: QLabel = QLabel(subtitle)
        self.sub_label.setWordWrap(True)
        self.sub_label.setStyleSheet(
            f"""
            color: {self.accent_color.name()}; 
            font-size: 8.5pt; 
            font-weight: 600;
            """
        )
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
        layout.addWidget(self.sub_label)
        
        self.set_hover_style(False)

    def set_hover_style(self, hovered: Any):
        border: Any = self.accent_color.name() if hovered else DarkPalette.BORDER.name()
        bg: Any = DarkPalette.BG_LIGHT.name() if hovered else DarkPalette.BG_MEDIUM.name()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)

    def enterEvent(self, event: Any):
        self.set_hover_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event: Any):
        self.set_hover_style(False)
        super().leaveEvent(event)