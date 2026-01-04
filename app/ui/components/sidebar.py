from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QProgressBar, QFrame
)
from PyQt6.QtCore import pyqtSignal, QTimer, QPropertyAnimation, Qt, QEasingCurve
from typing import Dict, Any, Optional
from datetime import datetime

from app.ui.styles import StyleSheet, DarkPalette

class SidebarWidget(QWidget):
    filters_changed = pyqtSignal(dict)
    refresh_requested = pyqtSignal()
    collapsed_toggled = pyqtSignal(bool)
    export_requested = pyqtSignal()

    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        self.is_collapsed: bool = False
        self.full_width: int = 320
        self.collapsed_width: int = 70
        
        self.setFixedWidth(self.full_width)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {DarkPalette.BG_MEDIUM.name()};
                border-right: 1px solid {DarkPalette.BORDER.name()};
            }}
            QLabel {{ 
                color: {DarkPalette.TEXT_SECONDARY.name()}; 
                font-size: 9pt; 
                border: none; 
                background: transparent;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 20, 15, 20)
        self.main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("⚙️ CONTROL PANEL")
        self.title_label.setStyleSheet("font-weight: 800; color: white; font-size: 11pt;")
        
        self.toggle_btn = QPushButton("≡")
        self.toggle_btn.setFixedSize(35, 35)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet(
            f"background: {DarkPalette.BG_LIGHT.name()}; color: white; "
            f"font-size: 14pt; border-radius: 5px; border: 1px solid {DarkPalette.BORDER.name()};"
        )
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_btn)
        self.main_layout.addLayout(header_layout)

        self._add_divider()

        self.user_box = QFrame()
        self.user_box.setStyleSheet(
            f"background: {DarkPalette.BG_LIGHT.name()}44; border-radius: 10px;"
        )
        user_l = QVBoxLayout(self.user_box)
        self.user_name = QLabel("👤 Admin User")
        self.user_name.setStyleSheet("font-weight: bold; color: white;")
        self.user_role = QLabel("System Administrator")
        self.user_role.setStyleSheet("font-size: 7pt; color: #3498db;")

        user_l.addWidget(self.user_name)
        user_l.addWidget(self.user_role)
        self.main_layout.addWidget(self.user_box)

        self.actions_group = self._create_group("🎯 Quick Actions")
        actions_layout = self.actions_group.layout()
        
        self.refresh_btn = QPushButton(" 🔄 Refresh Data")
        self.refresh_btn.setStyleSheet(StyleSheet.BUTTON)
        self.refresh_btn.clicked.connect(lambda: self._show_temp_message("✅ Refresh Signal Emitted"))
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)

        self.export_btn = QPushButton(" 📊 Export Report")
        self.export_btn.setStyleSheet(StyleSheet.BUTTON)
        self.export_btn.clicked.connect(lambda: self._show_temp_message("📄 Preparing Export..."))
        self.export_btn.clicked.connect(self.export_requested.emit)

        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addWidget(self.export_btn)
        self.main_layout.addWidget(self.actions_group)

        self.filters_group = self._create_group("🔧 Global Filters")
        filter_layout = self.filters_group.layout()
        
        self.region_combo = QComboBox()
        self.region_combo.setStyleSheet(StyleSheet.COMBO_BOX)
        self._load_regions()
        self.region_combo.currentTextChanged.connect(self._handle_filter_change)
        
        self.segment_combo = QComboBox()
        self.segment_combo.setStyleSheet(StyleSheet.COMBO_BOX)
        self._load_segments()
        self.segment_combo.currentTextChanged.connect(self._handle_filter_change)
        
        filter_layout.addWidget(QLabel("REGION:"))
        filter_layout.addWidget(self.region_combo)
        filter_layout.addWidget(QLabel("SEGMENT:"))
        filter_layout.addWidget(self.segment_combo)
        self.main_layout.addWidget(self.filters_group)

        self.health_group = self._create_group("📡 System Health")
        health_layout = self.health_group.layout()
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(24)
        self.cpu_bar.setFixedHeight(6)
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #3498db; border-radius: 3px; }")
        
        health_layout.addWidget(QLabel("SERVER LOAD:"))
        health_layout.addWidget(self.cpu_bar)
        self.main_layout.addWidget(self.health_group)

        self.main_layout.addStretch()

        self.status_label = QLabel("System Ready")
        self.status_label.setStyleSheet("color: #888; font-style: italic; margin-bottom: 5px;")
        self.main_layout.addWidget(self.status_label)

        self.status_panel = self._create_status_panel()
        self.main_layout.addWidget(self.status_panel)

    def _create_group(self, title_text: str) -> QWidget:
        group = QWidget()
        l = QVBoxLayout(group)
        l.setContentsMargins(0, 5, 0, 5)
        l.setSpacing(8)
        
        lbl = QLabel(title_text)
        lbl.setStyleSheet("font-weight: bold; color: white; margin-bottom: 2px;")
        l.addWidget(lbl)
        
        group.title_label = lbl 
        return group

    def toggle_collapse(self) -> None:
        self.is_collapsed = not self.is_collapsed
        start_w = self.width()
        end_w = self.collapsed_width if self.is_collapsed else self.full_width
        
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(250)
        self.anim.setStartValue(start_w)
        self.anim.setEndValue(end_w)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.anim.start()
        
        self.setFixedWidth(end_w)

        visible = not self.is_collapsed
        self.title_label.setVisible(visible)
        self.user_box.setVisible(visible)
        self.status_panel.setVisible(visible)
        self.filters_group.setVisible(visible)
        self.health_group.setVisible(visible)
        self.actions_group.title_label.setVisible(visible)
        self.status_label.setVisible(visible)
        self.export_btn.setVisible(visible)

        if self.is_collapsed:
            self.refresh_btn.setText("🔄")
            self.toggle_btn.setText("»")
            self.main_layout.setContentsMargins(10, 20, 10, 20)
        else:
            self.refresh_btn.setText(" 🔄 Refresh Data")
            self.toggle_btn.setText("≡")
            self.main_layout.setContentsMargins(15, 20, 15, 20)
            
        self.collapsed_toggled.emit(self.is_collapsed)

    def _show_temp_message(self, msg: str, timeout: int = 3000):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        QTimer.singleShot(timeout, lambda: self.status_label.setText("System Ready"))
        QTimer.singleShot(timeout, lambda: self.status_label.setStyleSheet("color: #888; font-style: italic;"))

    def _handle_filter_change(self) -> None:
        data = {
            "region": self.region_combo.currentText(),
            "segment": self.segment_combo.currentText()
        }
        self.filters_changed.emit(data)

    def _add_divider(self) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {DarkPalette.BORDER.name()}; max-height: 1px; border: none;")
        self.main_layout.addWidget(line)

    def _create_status_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("StatusPanel")
        panel.setStyleSheet(
            f"#StatusPanel {{ "
            f"background-color: {DarkPalette.BG_LIGHT.name()}; "
            f"border-left: 4px solid {DarkPalette.ACCENT_GREEN.name()}; "
            f"border-radius: 8px; }}"
        )
        l = QVBoxLayout(panel)
        l.setContentsMargins(10, 10, 10, 10)
        
        self.stats_lbl = QLabel("DB: CONNECTING...")
        self.uptime_lbl = QLabel(f"SYNC: {datetime.now().strftime('%H:%M:%S')}")
        self.uptime_lbl.setStyleSheet("font-size: 8pt; color: #666;")
        
        l.addWidget(self.stats_lbl)
        l.addWidget(self.uptime_lbl)
        
        QTimer.singleShot(1000, self._update_stats)
        return panel

    def _update_stats(self) -> None:
        try:
            tc = self.services['customer'].count_all()
            ta = self.services['account'].count_all()
            self.stats_lbl.setText(f"DATABASE: {tc + ta:,} RECS")
            self.uptime_lbl.setText(f"SYNC: {datetime.now().strftime('%H:%M:%S')}")
        except Exception:
            self.stats_lbl.setText("DATABASE: OFFLINE")
            self.status_panel.setStyleSheet(self.status_panel.styleSheet().replace(DarkPalette.ACCENT_GREEN.name(), "#e74c3c"))
            
        QTimer.singleShot(10000, self._update_stats)

    def _load_regions(self) -> None:
        self.region_combo.addItem("All Regions")
        try:
            regions = self.services['branch'].get_all_regions()
            if regions: self.region_combo.addItems(regions)
        except Exception: pass

    def _load_segments(self) -> None:
        self.segment_combo.addItem("All Segments")
        try:
            segments = self.services['customer'].get_all_segments()
            if segments: self.segment_combo.addItems(segments)
        except Exception: pass