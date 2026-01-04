from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QProgressBar, QFrame
)

from PyQt6.QtCore import pyqtSignal, QTimer, QPropertyAnimation, Qt

from typing import Dict, Any, Optional
from datetime import datetime

from app.ui.styles import StyleSheet, DarkPalette

class SidebarWidget(QWidget):
    filters_changed = pyqtSignal(dict)
    refresh_requested = pyqtSignal()
    collapsed_toggled = pyqtSignal(bool)

    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        self.is_collapsed: bool = False
        self.full_width: int = 280
        self.collapsed_width: int = 70
        
        self.main_layout: QVBoxLayout
        self.title_label: QLabel
        self.toggle_btn: QPushButton
        self.user_box: QFrame
        self.user_name: QLabel
        self.user_role: QLabel
        self.actions_group: QWidget
        self.refresh_btn: QPushButton
        self.filters_group: QWidget
        self.region_combo: QComboBox
        self.segment_combo: QComboBox
        self.health_group: QWidget
        self.cpu_bar: QProgressBar
        self.status_panel: QFrame
        self.stats_lbl: QLabel
        self.uptime_lbl: QLabel
        self.anim: QPropertyAnimation
        
        self.setFixedWidth(self.full_width)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {DarkPalette.BG_MEDIUM.name()};
                border-right: 1px solid {DarkPalette.BORDER.name()};
            }}
            QLabel {{ color: {DarkPalette.TEXT_SECONDARY.name()}; font-size: 9pt; border: none; }}
        """)
        self.init_ui()
    
    def init_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 15, 10, 15)
        self.main_layout.setSpacing(10)

        header_layout: QHBoxLayout = QHBoxLayout()
        self.title_label = QLabel("⚙️ CONTROL PANEL")
        self.title_label.setStyleSheet(
            """
            font-weight: 800; 
            color: white; 
            font-size: 11pt;
            """)
        
        self.toggle_btn = QPushButton("≡")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet(
            f"background: {DarkPalette.BG_LIGHT.name()}; "
            f"color: white; font-size: 16pt; border-radius: 5px;"
        )
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_btn)
        self.main_layout.addLayout(header_layout)

        self._add_divider()

        self.user_box = QFrame()
        self.user_box.setStyleSheet(
            f"""
            background: {DarkPalette.BG_LIGHT.name()}44; 
            border-radius: 10px;
            """
        )
        user_l: QVBoxLayout = QVBoxLayout(self.user_box)
        self.user_name = QLabel("👤 Admin User")
        self.user_name.setStyleSheet(
            """
            font-weight: bold; 
            color: white;
            """
        )
        self.user_role = QLabel("System Administrator")
        self.user_role.setStyleSheet(
            """
            font-size: 7pt; 
            color: palette(accent);
            """
        )
        user_l.addWidget(self.user_name)
        user_l.addWidget(self.user_role)
        self.main_layout.addWidget(self.user_box)

        self.actions_group = self._create_group("🎯 Quick Actions")
        
        self.refresh_btn = QPushButton(" 🔄 Refresh Data")
        self.refresh_btn.setStyleSheet(StyleSheet.BUTTON)
        self.refresh_btn.clicked.connect(lambda: print("DEBUG: Refresh Signal Emitted"))
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        
        export_btn: QPushButton = QPushButton(" 📊 Export Report")
        export_btn.setStyleSheet(StyleSheet.BUTTON)
        
        layout = self.actions_group.layout()
        if layout:
            layout.addWidget(self.refresh_btn)
            layout.addWidget(export_btn)
        self.main_layout.addWidget(self.actions_group)

        self.filters_group = self._create_group("🔧 Global Filters")
        
        self.region_combo = QComboBox()
        self.region_combo.setStyleSheet(StyleSheet.COMBO_BOX)
        self._load_regions()
        self.region_combo.currentTextChanged.connect(self._handle_filter_change)
        
        self.segment_combo = QComboBox()
        self.segment_combo.setStyleSheet(StyleSheet.COMBO_BOX)
        self._load_segments()
        self.segment_combo.currentTextChanged.connect(self._handle_filter_change)
        
        filter_layout = self.filters_group.layout()
        if filter_layout:
            filter_layout.addWidget(QLabel("REGION:"))
            filter_layout.addWidget(self.region_combo)
            filter_layout.addWidget(QLabel("SEGMENT:"))
            filter_layout.addWidget(self.segment_combo)
        self.main_layout.addWidget(self.filters_group)

        self.health_group = self._create_group("📡 System Health")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(24)
        self.cpu_bar.setFixedHeight(8)
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #3498db; }")
        
        health_layout = self.health_group.layout()
        if health_layout:
            health_layout.addWidget(QLabel("SERVER LOAD:"))
            health_layout.addWidget(self.cpu_bar)
        self.main_layout.addWidget(self.health_group)

        self.main_layout.addStretch()

        self.status_panel = self._create_status_panel()
        self.main_layout.addWidget(self.status_panel)

    def _create_group(self, title_text: str) -> QWidget:
        group: QWidget = QWidget()
        l: QVBoxLayout = QVBoxLayout(group)
        l.setContentsMargins(0, 5, 0, 5)
        lbl: QLabel = QLabel(title_text)
        lbl.setStyleSheet(
            """
            font-weight: bold; color: white; margin-bottom: 2px;
            """
        )
        l.addWidget(lbl)
        group.title_label = lbl
        return group

    def toggle_collapse(self) -> None:
        self.is_collapsed = not self.is_collapsed
        new_width: int = self.collapsed_width if self.is_collapsed else self.full_width
        
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(200)
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(new_width)
        self.anim.start()
        self.setFixedWidth(new_width)

        self.title_label.setVisible(not self.is_collapsed)
        self.user_box.setVisible(not self.is_collapsed)
        self.status_panel.setVisible(not self.is_collapsed)
        self.actions_group.title_label.setVisible(not self.is_collapsed)
        self.filters_group.setVisible(not self.is_collapsed)
        self.health_group.setVisible(not self.is_collapsed)
        
        if self.is_collapsed:
            self.refresh_btn.setText("🔄")
            self.toggle_btn.setText("»")
        else:
            self.refresh_btn.setText(" 🔄 Refresh Data")
            self.toggle_btn.setText("≡")
            
        self.collapsed_toggled.emit(self.is_collapsed)

    def _handle_filter_change(self) -> None:
        data: Dict[str, str] = {
            "region": self.region_combo.currentText(),
            "segment": self.segment_combo.currentText()
        }
        print(f"DEBUG: Filters changed -> {data}")
        self.filters_changed.emit(data)

    def _add_divider(self) -> None:
        line: QFrame = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(
            f"background-color: {DarkPalette.BORDER.name()}; max-height: 1px;"
        )
        self.main_layout.addWidget(line)

    def _create_status_panel(self) -> QFrame:
        panel: QFrame = QFrame()
        panel.setObjectName("StatusPanel")
        panel.setStyleSheet(
            f"#StatusPanel {{ "
            f"background-color: {DarkPalette.BG_LIGHT.name()}; "
            f"border-left: 4px solid {DarkPalette.ACCENT_GREEN.name()}; "
            f"border-radius: 8px; }}"
        )
        l: QVBoxLayout = QVBoxLayout(panel)
        self.stats_lbl = QLabel("DB: CONNECTING...")
        self.uptime_lbl = QLabel(f"SYNC: {datetime.now().strftime('%H:%M:%S')}")
        l.addWidget(self.stats_lbl)
        l.addWidget(self.uptime_lbl)
        QTimer.singleShot(1000, self._update_stats)
        return panel

    def _update_stats(self) -> None:
        try:
            tc: int = self.services['customer'].count_all()
            ta: int = self.services['account'].count_all()
            self.stats_lbl.setText(f"DATABASE: {tc + ta:,} RECS")
            self.uptime_lbl.setText(f"SYNC: {datetime.now().strftime('%H:%M:%S')}")
        except Exception:
            self.stats_lbl.setText("DATABASE: OFFLINE")
        QTimer.singleShot(10000, self._update_stats)

    def _load_regions(self) -> None:
        self.region_combo.addItem("All Regions")
        try:
            regions = self.services['branch'].get_all_regions()
            if regions:
                self.region_combo.addItems(regions)
        except Exception:
            pass

    def _load_segments(self) -> None:
        self.segment_combo.addItem("All Segments")
        try:
            segments = self.services['customer'].get_all_segments()
            if segments:
                self.segment_combo.addItems(segments)
        except Exception:
            pass