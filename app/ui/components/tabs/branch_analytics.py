from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QComboBox,
    QStackedWidget, QTableWidget, QTableWidgetItem, QToolTip,
    QFrame, QLabel, QCheckBox, QHeaderView, QPushButton, QMessageBox
)

from PyQt6.QtCharts import (
    QChartView, QChart,
    QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
)

from PyQt6.QtGui import QPainter, QCursor
from PyQt6.QtCore import QTimer, Qt

import numpy as np
from typing import Dict, List, Any, Optional

from app.ui.styles import StyleSheet, DarkPalette
from app.ui.components.cards.metric import MetricCard

class BranchAnalyticsTab(QWidget):
    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        
        self.kpi_layout: QHBoxLayout
        self.display_stack: QStackedWidget
        self.chart_view: QChartView
        self.table: QTableWidget
        self.btn_chart: QPushButton
        self.btn_table: QPushButton
        self.view_type: QComboBox
        self.stat_checks: Dict[str, QCheckBox]
        self.load_btn: QPushButton
        
        self.init_ui()
        QTimer.singleShot(150, self.load_data)
    
    def init_ui(self) -> None:
        main_layout: QHBoxLayout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        left_panel: QVBoxLayout = QVBoxLayout()
        
        self.kpi_layout = QHBoxLayout()
        left_panel.addLayout(self.kpi_layout)
        
        self.display_stack = QStackedWidget()
        self._setup_views()
        left_panel.addWidget(self.display_stack)
        
        main_layout.addLayout(left_panel, stretch=4)
        
        sidebar: QFrame = self._create_sidebar()
        main_layout.addWidget(sidebar)

    def _setup_views(self) -> None:
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setMouseTracking(True)
        self.chart_view.setStyleSheet(
            f"""
            background: {DarkPalette.BG_MEDIUM.name()}; 
            border-radius: 15px;
            """
        )
        
        self.table = QTableWidget()
        self.table.setStyleSheet(StyleSheet.TABLE)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Branch Name", "Code", "Region", "Accounts"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.display_stack.addWidget(self.chart_view)
        self.display_stack.addWidget(self.table)

    def _create_sidebar(self) -> QFrame:
        sidebar: QFrame = QFrame()
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet(
            f"""
            background: {DarkPalette.BG_LIGHT.name()}; 
            border-radius: 20px; 
            border: 1px solid {DarkPalette.BORDER.name()};
            """
        )
        side_layout: QVBoxLayout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 25, 20, 25)

        side_layout.addWidget(self._create_section_title("VIEW CONFIGURATION"))
        view_nav: QHBoxLayout = QHBoxLayout()
        self.btn_chart = self._create_toggle_btn("Analytics", True, 0)
        self.btn_table = self._create_toggle_btn("Data List", False, 1)
        view_nav.addWidget(self.btn_chart)
        view_nav.addWidget(self.btn_table)
        side_layout.addLayout(view_nav)

        side_layout.addSpacing(15)

        side_layout.addWidget(QLabel("Analysis Mode"))
        self.view_type = QComboBox()
        self.view_type.addItems(["Account Distribution", "Regional Performance"])
        self.view_type.setStyleSheet(StyleSheet.COMBO_BOX)
        side_layout.addWidget(self.view_type)

        side_layout.addSpacing(15)

        side_layout.addWidget(self._create_section_title("STATISTICS TO SHOW"))
        metrics_grid: QGridLayout = QGridLayout()
        self.stat_checks = {
            'mean': QCheckBox("Average"),
            'std': QCheckBox("Std Dev"),
            'min': QCheckBox("Min"),
            'max': QCheckBox("Max")
        }
        for i, (key, cb) in enumerate(self.stat_checks.items()):
            cb.setChecked(True)
            cb.setStyleSheet("color: white; font-size: 9pt;")
            cb.stateChanged.connect(self.load_data)
            metrics_grid.addWidget(cb, i // 2, i % 2)
        side_layout.addLayout(metrics_grid)

        side_layout.addStretch()

        self.load_btn = QPushButton("REFRESH BRANCH DATA")
        self.load_btn.setFixedHeight(50)
        self.load_btn.setStyleSheet(
            f"""
            background: {DarkPalette.ACCENT_BLUE.name()}; 
            color: white; 
            font-weight: bold; 
            border-radius: 12px;
            """
        )
        self.load_btn.clicked.connect(self.load_data)
        side_layout.addWidget(self.load_btn)
        
        return sidebar

    def _create_toggle_btn(self, text: str, checked: bool, index: int) -> QPushButton:
        btn: QPushButton = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setStyleSheet(StyleSheet.BUTTON)
        btn.clicked.connect(lambda: self._toggle_view(index))
        return btn

    def _toggle_view(self, index: int) -> None:
        self.display_stack.setCurrentIndex(index)
        self.btn_chart.setChecked(index == 0)
        self.btn_table.setChecked(index == 1)

    def _create_section_title(self, text: str) -> QLabel:
        lbl: QLabel = QLabel(text)
        lbl.setStyleSheet(
            f"""
            color: {DarkPalette.ACCENT_BLUE.name()}; 
            font-weight: 800; 
            font-size: 8pt; 
            letter-spacing: 1px; 
            margin-top: 10px;
            """
        )
        return lbl

    def clear_kpi(self) -> None:
        while (item := self.kpi_layout.takeAt(0)) is not None:
            if widget := item.widget():
                widget.deleteLater()

    def load_data(self) -> None:
        try:
            self.clear_kpi()
            branches_data: List[Dict[str, Any]] = self.services['branch'].get_branches_by_account_count(min_accounts=0)
            
            if not branches_data:
                self.chart_view.setChart(QChart())
                return

            counts: List[int] = [item['account_count'] for item in branches_data]
            self._fill_kpi(counts)

            self._fill_chart(branches_data)

            self._fill_table(branches_data)

        except Exception as e:
            QMessageBox.critical(self, "Branch Analytics Error", str(e))

    def _fill_kpi(self, counts: List[int]) -> None:
        if self.stat_checks['mean'].isChecked():
            self.kpi_layout.addWidget(MetricCard("Avg Accounts", f"{np.mean(counts):.1f}", "Per Branch"))
        if self.stat_checks['std'].isChecked():
            self.kpi_layout.addWidget(MetricCard("Consistency", f"{np.std(counts):.1f}", "Std Deviation", DarkPalette.ACCENT_BLUE))
        if self.stat_checks['min'].isChecked():
            self.kpi_layout.addWidget(MetricCard("Min Load", str(min(counts)), "Smallest", DarkPalette.ACCENT_ORANGE))
        if self.stat_checks['max'].isChecked():
            self.kpi_layout.addWidget(MetricCard("Max Load", str(max(counts)), "Largest", DarkPalette.ACCENT_GREEN))
        self.kpi_layout.addStretch()

    def _fill_chart(self, branches_data: List[Dict[str, Any]]) -> None:
        chart: QChart = QChart()
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundVisible(False)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        series: QBarSeries = QBarSeries()
        bar_set: QBarSet = QBarSet("Accounts")
        bar_set.setColor(DarkPalette.ACCENT_BLUE)
        
        categories: List[str] = []
        for item in branches_data:
            bar_set.append(item['account_count'])
            categories.append(item['branch'].branch_code)
        
        series.append(bar_set)
        
        series.hovered.connect(
            lambda hovered, index: self._handle_bar_hover(hovered, index, branches_data)
        )
        
        chart.addSeries(series)

        axis_x: QBarCategoryAxis = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y: QValueAxis = QValueAxis()
        axis_y.setTitleText("Total Accounts")
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().hide()
        self.chart_view.setChart(chart)

    def _handle_bar_hover(
        self, 
        is_hovered: bool, 
        index: int, 
        branches_data: List[Dict[str, Any]]
    ) -> None:
        if is_hovered and index < len(branches_data):
            data: Dict[str, Any] = branches_data[index]
            branch: Any = data['branch']
            text: str = (
                f"<b>{branch.branch_name}</b><br>"
                f"Region: {branch.region or 'N/A'}<br>"
                f"Accounts: {data['account_count']}"
            )
            QToolTip.showText(QCursor.pos(), text)
        else:
            QToolTip.hideText()

    def _fill_table(self, branches_data: List[Dict[str, Any]]) -> None:
        self.table.setRowCount(len(branches_data))
        for i, item in enumerate(branches_data):
            branch: Any = item['branch']
            self.table.setItem(i, 0, QTableWidgetItem(branch.branch_name))
            self.table.setItem(i, 1, QTableWidgetItem(branch.branch_code))
            self.table.setItem(i, 2, QTableWidgetItem(branch.region or 'N/A'))
            count_item: QTableWidgetItem = QTableWidgetItem(str(item['account_count']))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 3, count_item)