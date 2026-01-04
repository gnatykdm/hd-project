from PyQt6.QtGui import QColor

class DarkPalette:
    BG_DARK: QColor = QColor("#0E1217")
    BG_MEDIUM: QColor = QColor("#1C2127")
    BG_LIGHT: QColor = QColor("#262C34")
    BORDER: QColor = QColor("#383F47")
    
    TEXT_PRIMARY: QColor = QColor("#F5F8FA")
    TEXT_SECONDARY: QColor = QColor("#A7B6C2")
    TEXT_MUTED: QColor = QColor("#8A9BA8")
    
    ACCENT_BLUE: QColor = QColor("#4A90E2")
    ACCENT_GREEN: QColor = QColor("#0F9960")
    ACCENT_PURPLE: QColor = QColor("#8E44AD")
    ACCENT_YELLOW: QColor = QColor("#F1C40F")
    ACCENT_ORANGE: QColor = QColor("#F29D49")
    ACCENT_RED: QColor = QColor("#D13212")

class StyleSheet:
    MAIN_WINDOW: str = f"""
        QMainWindow {{
            background-color: {DarkPalette.BG_DARK.name()};
        }}
        QWidget {{
            background-color: {DarkPalette.BG_DARK.name()};
            color: {DarkPalette.TEXT_PRIMARY.name()};
            font-family: 'Segoe UI', Arial;
            font-size: 10pt;
        }}
    """
    
    HEADER_WIDGET: str = f"""
        QWidget {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {DarkPalette.BG_MEDIUM.name()},
                stop:1 {DarkPalette.BG_LIGHT.name()});
            border: 1px solid {DarkPalette.BORDER.name()};
            border-radius: 4px;
            padding: 20px;
        }}
        QLabel {{
            background: transparent;
            color: {DarkPalette.TEXT_PRIMARY.name()};
        }}
    """
    
    METRIC_CARD: str = f"""
        QFrame {{
            background-color: {DarkPalette.BG_MEDIUM.name()};
            border: 1px solid {DarkPalette.BORDER.name()};
            border-radius: 4px;
            padding: 15px;
        }}
        QFrame:hover {{
            background-color: {DarkPalette.BG_LIGHT.name()};
            border-color: {DarkPalette.ACCENT_BLUE.name()};
        }}
        QLabel {{
            background: transparent;
        }}
    """
    
    BUTTON: str = f"""
        QPushButton {{
            background-color: {DarkPalette.BG_LIGHT.name()};
            color: {DarkPalette.TEXT_PRIMARY.name()};
            border: 1px solid {DarkPalette.BORDER.name()};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {DarkPalette.ACCENT_BLUE.name()};
            border-color: {DarkPalette.ACCENT_BLUE.name()};
        }}
        QPushButton:pressed {{
            background-color: #3A7AC2;
        }}
    """

    CONTEXT_MENU: str = f"""
        QMenu {{
            background-color: {DarkPalette.BG_LIGHT.name()};
            color: white;
            border: 1px solid {DarkPalette.BORDER.name()};
            border-radius: 10px;
            padding: 5px;
        }}
        QMenu::item {{
            padding: 8px 30px 8px 10px;
            border-radius: 5px;
            margin: 2px;
            font-size: 9pt;
        }}
        QMenu::item:selected {{
            background-color: {DarkPalette.ACCENT_BLUE.name()};
            color: white;
        }}
        QMenu::separator {{
            height: 1px;
            background: {DarkPalette.BORDER.name()};
            margin: 5px 10px;
        }}
        QMenu::icon {{
            padding-left: 10px;
        }}
    """
    
    COMBO_BOX: str = f"""
        QComboBox {{
            background-color: {DarkPalette.BG_LIGHT.name()};
            border: 1px solid {DarkPalette.BORDER.name()};
            border-radius: 4px;
            padding: 6px;
            color: {DarkPalette.TEXT_PRIMARY.name()};
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {DarkPalette.TEXT_MUTED.name()};
        }}
        QComboBox QAbstractItemView {{
            background-color: {DarkPalette.BG_LIGHT.name()};
            border: 1px solid {DarkPalette.BORDER.name()};
            selection-background-color: {DarkPalette.ACCENT_BLUE.name()};
            color: {DarkPalette.TEXT_PRIMARY.name()};
        }}
    """
    
    LINE_EDIT: str = f"""
        QLineEdit {{
            background-color: {DarkPalette.BG_LIGHT.name()};
            border: 1px solid {DarkPalette.BORDER.name()};
            border-radius: 4px;
            padding: 6px;
            color: {DarkPalette.TEXT_PRIMARY.name()};
        }}
        QLineEdit:focus {{
            border-color: {DarkPalette.ACCENT_BLUE.name()};
        }}
    """
    
    TABLE: str = f"""
        QTableWidget {{
            background-color: {DarkPalette.BG_MEDIUM.name()};
            border: 1px solid {DarkPalette.BORDER.name()};
            border-radius: 4px;
            gridline-color: {DarkPalette.BORDER.name()};
            color: {DarkPalette.TEXT_PRIMARY.name()};
        }}
        QTableWidget::item {{
            padding: 5px;
        }}
        QTableWidget::item:selected {{
            background-color: {DarkPalette.ACCENT_BLUE.name()};
        }}
        QHeaderView::section {{
            background-color: {DarkPalette.BG_LIGHT.name()};
            color: {DarkPalette.TEXT_MUTED.name()};
            padding: 8px;
            border: none;
            border-bottom: 1px solid {DarkPalette.BORDER.name()};
            font-weight: 600;
            text-transform: uppercase;
            font-size: 9pt;
        }}
    """
    
    TAB_WIDGET: str = f"""
        QTabWidget::pane {{
            border: 1px solid {DarkPalette.BORDER.name()};
            background-color: {DarkPalette.BG_DARK.name()};
            border-radius: 4px;
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {DarkPalette.TEXT_MUTED.name()};
            padding: 10px 20px;
            margin-right: 2px;
            border-radius: 3px;
        }}
        QTabBar::tab:selected {{
            background-color: {DarkPalette.ACCENT_BLUE.name()};
            color: white;
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {DarkPalette.BG_LIGHT.name()};
        }}
    """
    
    SCROLL_AREA: str = f"""
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            border: none;
            background: {DarkPalette.BG_MEDIUM.name()};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {DarkPalette.BORDER.name()};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {DarkPalette.TEXT_MUTED.name()};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
    """
