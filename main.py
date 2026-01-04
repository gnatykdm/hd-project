"""
Main application entry point for MORDOR Data Intelligence System.

This module initializes the Qt application, configures global settings,
and launches the main window.
"""

import sys
from typing import NoReturn, List
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QPolygonF
from PyQt6.QtCore import Qt, QPointF

from app.ui.components.window import MainWindow


def main() -> NoReturn:
    """
    Initialize and run the main application.
    
    This function:
    1. Creates the QApplication instance
    2. Configures the application style, font, and icon
    3. Creates and displays the main window in fullscreen
    4. Enters the Qt event loop
    
    Returns:
        NoReturn: This function never returns normally; it exits via sys.exit()
    """
    args: List[str] = sys.argv
    
    app: QApplication = QApplication(args)
    
    # Set application metadata
    app.setApplicationName("MORDOR")
    app.setOrganizationName("Data Intelligence")
    
    # Set Fusion style
    app.setStyle('Fusion')
    
    # Configure font
    font: QFont = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Set application icon
    icon_path: Path = Path(__file__).parent / "assets" / "icon.png"
    
    if icon_path.exists():
        # Load icon from file
        app_icon: QIcon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
    else:
        # Create fallback icon with white diamond
        pixmap: QPixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter: QPainter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw white diamond (rotated square)
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Diamond points (center of 64x64 canvas)
        from PyQt6.QtCore import QPointF
        diamond_points = [
            QPointF(32, 8),   # Top
            QPointF(56, 32),  # Right
            QPointF(32, 56),  # Bottom
            QPointF(8, 32)    # Left
        ]
        
        from PyQt6.QtGui import QPolygonF
        diamond: QPolygonF = QPolygonF(diamond_points)
        painter.drawPolygon(diamond)
        painter.end()
        
        app_icon = QIcon(pixmap)
        app.setWindowIcon(app_icon)
    
    # Create main window
    window: MainWindow = MainWindow()
    
    # Show in fullscreen mode
    window.showFullScreen()
    
    # Run application
    exit_code: int = app.exec()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()