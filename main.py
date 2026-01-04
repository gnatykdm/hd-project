"""
Main application entry point for MORDOR Data Intelligence System.

This module initializes the Qt application, configures global settings,
and launches the main window.

App: Mordor v1.0
Developed by: Dmytro Gnatyk
"""

import sys
from typing import NoReturn, List

from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QPolygonF
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPointF

from app.ui.components.window import MainWindow

def main() -> NoReturn:
    args: List[str] = sys.argv
    
    app: QApplication = QApplication(args)
    
    app.setApplicationName("MORDOR")
    app.setOrganizationName("Data Intelligence")
    
    app.setStyle('Fusion')
    
    font: QFont = QFont("Segoe UI", 10)
    app.setFont(font)
    
    pixmap: QPixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
        
    painter: QPainter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    painter.setBrush(QColor("#ffffff"))
    painter.setPen(Qt.PenStyle.NoPen)
        
    diamond_points = [
        QPointF(32, 8),
        QPointF(56, 32),
        QPointF(32, 56),
        QPointF(8, 32)
    ]
        
    diamond: QPolygonF = QPolygonF(diamond_points)
    painter.drawPolygon(diamond)
    painter.end()
        
    app_icon = QIcon(pixmap)
    app.setWindowIcon(app_icon)

    window: MainWindow = MainWindow()
    window.show()

    exit_code: int = app.exec()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()