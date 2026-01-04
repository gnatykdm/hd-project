from typing import Dict, List, Any, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, 
    QDateEdit, QStackedWidget, QTableWidget, QTableWidgetItem, QToolTip,
    QFrame, QLabel, QCheckBox, QComboBox, QHeaderView, QPushButton
)

from PyQt6.QtCharts import (
    QChartView, QChart, QPieSeries, QPieSlice,
    QBarSeries, QBarSet, QBarCategoryAxis,
)

from PyQt6.QtGui import QPainter, QBrush, QCursor
from PyQt6.QtCore import QTimer, QDate, Qt

from datetime import datetime
import numpy as np

from app.ui.styles import StyleSheet, DarkPalette
from app.ui.components.cards.metric import MetricCard

class TransactionAnalyticsTab(QWidget):
    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        
        self.start_date_edit: QDateEdit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date_edit: QDateEdit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit.setCalendarPopup(True)
        
        self.metrics_container: QWidget
        self.metrics_area: QHBoxLayout
        self.view_stack: QStackedWidget
        self.chart_view: QChartView
        self.table: QTableWidget
        self.btn_chart: QPushButton
        self.btn_table: QPushButton
        self.chart_type_combo: QComboBox
        self.checks: Dict[str, QCheckBox]
        self.run_btn: QPushButton
        
        self.init_ui()
        QTimer.singleShot(150, self.run_analysis)

    def init_ui(self) -> None:
        main_layout: QHBoxLayout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        left_panel: QWidget = QWidget()
        left_layout: QVBoxLayout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.metrics_container = QWidget()
        self.metrics_container.setFixedHeight(130)
        self.metrics_area = QHBoxLayout(self.metrics_container)
        left_layout.addWidget(self.metrics_container)

        self.view_stack = QStackedWidget()
        self._setup_views()
        left_layout.addWidget(self.view_stack)

        right_panel: QFrame = self._create_control_panel()
        main_layout.addWidget(left_panel, stretch=4)
        main_layout.addWidget(right_panel, stretch=1)

    def _setup_views(self) -> None:
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setMouseTracking(True)
        self.chart_view.setStyleSheet(f"""
            background: {DarkPalette.BG_MEDIUM.name()}; 
            border-radius: 15px; 
            border: 1px solid {DarkPalette.BORDER.name()};
        """)
        
        self.table = QTableWidget()
        self.table.setStyleSheet(StyleSheet.TABLE)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Category", "Total Amount", "Count"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.view_stack.addWidget(self.chart_view)
        self.view_stack.addWidget(self.table)

    def _create_control_panel(self) -> QFrame:
        panel: QFrame = QFrame()
        panel.setFixedWidth(280)
        panel.setStyleSheet(f"background: {DarkPalette.BG_LIGHT.name()}; border-radius: 15px;")
        layout: QVBoxLayout = QVBoxLayout(panel)

        layout.addWidget(QLabel("DISPLAY MODE"))
        mode_layout: QHBoxLayout = QHBoxLayout()
        self.btn_chart = self._create_toggle_btn("CHART", True, lambda: self.toggle_view(0))
        self.btn_table = self._create_toggle_btn("TABLE", False, lambda: self.toggle_view(1))
        mode_layout.addWidget(self.btn_chart)
        mode_layout.addWidget(self.btn_table)
        layout.addLayout(mode_layout)

        layout.addSpacing(15)
        layout.addWidget(QLabel("CHART TYPE"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Donut", "Bars"])
        self.chart_type_combo.currentTextChanged.connect(self.run_analysis)
        layout.addWidget(self.chart_type_combo)

        layout.addSpacing(15)
        layout.addWidget(QLabel("ACTIVE METRICS"))
        self.checks = {
            'sum': QCheckBox("Total Volume"),
            'avg': QCheckBox("Average Spend"),
            'max': QCheckBox("Peak Category"),
            'cnt': QCheckBox("TX Count")
        }
        for cb in self.checks.values():
            cb.setChecked(True)
            cb.stateChanged.connect(self.run_analysis)
            layout.addWidget(cb)

        layout.addStretch()
        self.run_btn = QPushButton("🔄 REFRESH ANALYTICS")
        self.run_btn.setFixedHeight(45)
        self.run_btn.setStyleSheet(f"background-color: {DarkPalette.ACCENT_BLUE.name()}; color: white; border-radius: 10px; font-weight: bold;")
        self.run_btn.clicked.connect(self.run_analysis)
        layout.addWidget(self.run_btn)
        return panel

    def _create_toggle_btn(self, text: str, checked: bool, callback: Callable[[], None]) -> QPushButton:
        btn: QPushButton = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setStyleSheet(StyleSheet.BUTTON)
        btn.clicked.connect(callback)
        return btn

    def toggle_view(self, index: int) -> None:
        self.view_stack.setCurrentIndex(index)
        self.btn_chart.setChecked(index == 0)
        self.btn_table.setChecked(index == 1)

    def run_analysis(self) -> None:
        try:
            start_dt: datetime = datetime.combine(
                self.start_date_edit.date().toPyDate(), 
                datetime.min.time()
            )
            end_dt: datetime = datetime.combine(
                self.end_date_edit.date().toPyDate(), 
                datetime.max.time()
            )
            data: List[Dict[str, Any]] = self.services['transaction'].get_category_breakdown(
                start_date=start_dt, 
                end_date=end_dt
            )
            
            while (item := self.metrics_area.takeAt(0)) is not None:
                if widget := item.widget(): 
                    widget.deleteLater()

            if not data:
                self.table.setRowCount(0)
                self.chart_view.setChart(QChart())
                return

            self._fill_metrics(data)
            self._fill_chart(data)
            self._fill_table(data)
        except Exception as e:
            print(f"Analytics Error: {e}")

    def _fill_metrics(self, data: List[Dict[str, Any]]) -> None:
        totals: List[float] = [d['total'] for d in data]
        if self.checks['sum'].isChecked():
            self.metrics_area.addWidget(
                MetricCard("Volume", f"${sum(totals):,.0f}", "Total Turnover", DarkPalette.ACCENT_BLUE)
            )
        if self.checks['avg'].isChecked():
            self.metrics_area.addWidget(
                MetricCard("Average", f"${np.mean(totals):,.0f}", "By Category", DarkPalette.ACCENT_BLUE)
            )
        if self.checks['max'].isChecked():
            peak: Dict[str, Any] = max(data, key=lambda x: x['total'])
            self.metrics_area.addWidget(
                MetricCard("Peak", f"${peak['total']:,.0f}", peak['category'], DarkPalette.ACCENT_BLUE)
            )
        if self.checks['cnt'].isChecked():
            count_sum: int = sum(d['count'] for d in data)
            self.metrics_area.addWidget(
                MetricCard("TX Count", f"{count_sum:,}", "Total Ops", DarkPalette.ACCENT_BLUE)
            )
        self.metrics_area.addStretch()

    def _fill_chart(self, data: List[Dict[str, Any]]) -> None:
        chart: QChart = QChart()
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundVisible(False)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        main_color = DarkPalette.ACCENT_BLUE

        if self.chart_type_combo.currentText() == "Donut":
            series: QPieSeries = QPieSeries()
            series.setHoleSize(0.45)
            sorted_data: List[Dict[str, Any]] = sorted(data, key=lambda x: x['total'], reverse=True)
            
            for i, d in enumerate(sorted_data):
                slice: QPieSlice = series.append(d['category'], d['total'])
                slice.setBrush(QBrush(main_color.lighter(100 + (i * 15))))
                total_sum: float = sum(x['total'] for x in data)
                slice.setLabelVisible(d['total'] > total_sum * 0.07)
                
                self._bind_slice_events(slice)
                
            chart.addSeries(series)
        else:
            series: QBarSeries = QBarSeries()
            bar_set: QBarSet = QBarSet("Turnover")
            bar_set.setBrush(QBrush(main_color))
            
            categories: List[str] = []
            for d in sorted(data, key=lambda x: x['total'], reverse=True):
                bar_set.append(d['total'])
                categories.append(d['category'])
            
            series.append(bar_set)
            series.hovered.connect(
                lambda state, index: self._handle_bar_hover(state, index, categories)
            )
            
            chart.addSeries(series)
            axis_x: QBarCategoryAxis = QBarCategoryAxis()
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)

        self.chart_view.setChart(chart)

    def _bind_slice_events(self, slice: QPieSlice) -> None:
        slice.hovered.connect(lambda hovered: self._handle_slice_hover(hovered, slice))

    def _handle_slice_hover(self, is_hovered: bool, slice: QPieSlice) -> None:
        if is_hovered:
            slice.setExploded(True)
            label: str = f"<div style='color: white;'><b>{slice.label()}</b><br>Sum: ${slice.value():,.2f}</div>"
            QToolTip.showText(QCursor.pos(), label)
        else:
            slice.setExploded(False)
            QToolTip.hideText()

    def _handle_bar_hover(self, is_hovered: bool, index: int, categories: List[str]) -> None:
        if is_hovered and index < len(categories):
            category: str = categories[index]
            val: float = self.chart_view.chart().series()[0].barSets()[0].at(index)
            label: str = f"<b>{category}</b><br>Total: ${val:,.2f}"
            QToolTip.showText(QCursor.pos(), label)
        else:
            QToolTip.hideText()

    def _fill_table(self, data: List[Dict[str, Any]]) -> None:
        sorted_data: List[Dict[str, Any]] = sorted(data, key=lambda x: x['total'], reverse=True)
        self.table.setRowCount(len(sorted_data))
        for row, d in enumerate(sorted_data):
            self.table.setItem(row, 0, QTableWidgetItem(d['category']))
            self.table.setItem(row, 1, QTableWidgetItem(f"${d['total']:,.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(str(d['count'])))