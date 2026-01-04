from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QStackedWidget, QTableWidget, QTableWidgetItem, QToolTip,
    QFrame, QLabel, QCheckBox, QHeaderView, QPushButton, QSlider
)

from PyQt6.QtCharts import (
    QChartView, QChart,
    QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
)

from PyQt6.QtGui import QPainter, QCursor
from PyQt6.QtCore import QTimer, Qt

import numpy as np
from numpy.typing import NDArray

from app.ui.styles import StyleSheet, DarkPalette
from app.ui.components.cards.metric import MetricCard

class CustomerAnalyticsTab(QWidget):
    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        
        self.kpi_container: QWidget
        self.kpi_layout: QHBoxLayout
        self.display_stack: QStackedWidget
        self.chart_view: QChartView
        self.table: QTableWidget
        self.btn_show_chart: QPushButton
        self.btn_show_table: QPushButton
        self.stat_checks: Dict[str, QCheckBox]
        self.min_lbl: QLabel
        self.min_score: QSlider
        self.max_lbl: QLabel
        self.max_score: QSlider
        self.run_btn: QPushButton
        
        self.init_ui()
        QTimer.singleShot(150, self.run_analysis)

    def init_ui(self) -> None:
        main_layout: QHBoxLayout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        content_layout: QVBoxLayout = QVBoxLayout()
        
        self.kpi_container = QWidget()
        self.kpi_container.setFixedHeight(120)
        self.kpi_layout = QHBoxLayout(self.kpi_container)
        self.kpi_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.kpi_container)

        self.display_stack = QStackedWidget()
        self._setup_views()
        content_layout.addWidget(self.display_stack)
        
        main_layout.addLayout(content_layout, stretch=4)

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

        side_layout.addWidget(self._create_section_title("DISPLAY MODE"))
        view_nav: QHBoxLayout = QHBoxLayout()
        self.btn_show_chart = self._create_nav_btn("Graph", True, 0)
        self.btn_show_table = self._create_nav_btn("Table", False, 1)
        view_nav.addWidget(self.btn_show_chart)
        view_nav.addWidget(self.btn_show_table)
        side_layout.addLayout(view_nav)

        side_layout.addSpacing(20)

        side_layout.addWidget(self._create_section_title("STATISTICAL METRICS"))
        metrics_grid: QGridLayout = QGridLayout()
        self.stat_checks = {
            'mean': QCheckBox("Mean Score"),
            'std': QCheckBox("Std Dev"),
            'min': QCheckBox("Minimum"),
            'max': QCheckBox("Maximum")
        }
        for i, (key, cb) in enumerate(self.stat_checks.items()):
            cb.setChecked(True)
            cb.stateChanged.connect(self.run_analysis)
            metrics_grid.addWidget(cb, i // 2, i % 2)
        side_layout.addLayout(metrics_grid)

        side_layout.addSpacing(20)

        side_layout.addWidget(self._create_section_title("CREDIT SCORE FILTERS"))
        
        self.min_lbl = QLabel("Min Score: 400")
        self.min_score = QSlider(Qt.Orientation.Horizontal)
        self.min_score.setRange(300, 850)
        self.min_score.setValue(400)
        self.min_score.valueChanged.connect(lambda v: self.min_lbl.setText(f"Min Score: {v}"))
        
        self.max_lbl = QLabel("Max Score: 850")
        self.max_score = QSlider(Qt.Orientation.Horizontal)
        self.max_score.setRange(300, 850)
        self.max_score.setValue(850)
        self.max_score.valueChanged.connect(lambda v: self.max_lbl.setText(f"Max Score: {v}"))

        side_layout.addWidget(self.min_lbl)
        side_layout.addWidget(self.min_score)
        side_layout.addSpacing(10)
        side_layout.addWidget(self.max_lbl)
        side_layout.addWidget(self.max_score)

        side_layout.addStretch()

        self.run_btn = QPushButton("APPLY FILTERS")
        self.run_btn.setFixedHeight(50)
        self.run_btn.setStyleSheet(
            f"""
            background: {DarkPalette.ACCENT_BLUE.name()}; 
            color: white; 
            font-weight: bold; 
            border-radius: 12px;"""
        )
        self.run_btn.clicked.connect(self.run_analysis)
        side_layout.addWidget(self.run_btn)

        return sidebar

    def _create_nav_btn(self, text: str, checked: bool, index: int) -> QPushButton:
        btn: QPushButton = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedHeight(35)
        btn.setStyleSheet(StyleSheet.BUTTON)
        btn.clicked.connect(lambda: self._toggle_display(index))
        return btn

    def _toggle_display(self, index: int) -> None:
        self.display_stack.setCurrentIndex(index)
        self.btn_show_chart.setChecked(index == 0)
        self.btn_show_table.setChecked(index == 1)

    def _create_section_title(self, text: str) -> QLabel:
        lbl: QLabel = QLabel(text)
        lbl.setStyleSheet(
            f"""
            color: {DarkPalette.ACCENT_BLUE.name()}; 
            font-weight: 800; 
            font-size: 8pt; 
            letter-spacing: 1px;
            """
        )
        return lbl

    def run_analysis(self) -> None:
        try:
            self.clear_kpi()
            
            min_v: int = self.min_score.value()
            max_v: int = self.max_score.value()
            customers: List[Any] = self.services['customer'].get_by_credit_score_range(min_v, max_v)
            scores: List[float] = [c.credit_score for c in customers if c.credit_score is not None]

            if not scores:
                self.chart_view.setChart(QChart())
                self.table.setRowCount(0)
                return

            self._update_kpi_cards(scores)
            
            self._update_histogram(scores)

            self._update_table(customers)

        except Exception as e:
            print(f"Customer Analysis Error: {e}")

    def _update_kpi_cards(self, scores: List[float]) -> None:
        if self.stat_checks['mean'].isChecked():
            self.kpi_layout.addWidget(MetricCard("Average", f"{np.mean(scores):.0f}", "Mean Score"))
        if self.stat_checks['std'].isChecked():
            self.kpi_layout.addWidget(MetricCard("Volatility", f"{np.std(scores):.1f}", "Std Dev", DarkPalette.ACCENT_BLUE))
        if self.stat_checks['min'].isChecked():
            self.kpi_layout.addWidget(MetricCard("Minimum", str(min(scores)), "Lowest", DarkPalette.ACCENT_ORANGE))
        if self.stat_checks['max'].isChecked():
            self.kpi_layout.addWidget(MetricCard("Maximum", str(max(scores)), "Peak", DarkPalette.ACCENT_GREEN))
        self.kpi_layout.addStretch()

    def _update_histogram(self, scores: List[float]) -> None:
        chart: QChart = QChart()
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundVisible(False)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        series: QBarSeries = QBarSeries()
        bar_set: QBarSet = QBarSet("Frequency")
        bar_set.setColor(DarkPalette.ACCENT_BLUE)

        counts: NDArray[np.int_]
        bins: NDArray[np.float_]
        counts, bins = np.histogram(scores, bins=6)
        
        for count in counts:
            bar_set.append(float(count))
        
        series.append(bar_set)
        
        categories: List[str] = [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(len(bins)-1)]
        series.hovered.connect(
            lambda hovered, index: self._handle_bar_hover(hovered, index, categories, counts)
        )
        
        chart.addSeries(series)

        axis_x: QBarCategoryAxis = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y: QValueAxis = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setTitleText("Number of Customers")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().hide()
        self.chart_view.setChart(chart)

    def _handle_bar_hover(
        self, 
        is_hovered: bool, 
        index: int, 
        categories: List[str], 
        counts: NDArray[np.int_]
    ) -> None:
        if is_hovered and index < len(categories):
            val: int = int(counts[index])
            QToolTip.showText(
                QCursor.pos(), 
                f"<b>Range: {categories[index]}</b><br>Customers: {val}"
            )
        else:
            QToolTip.hideText()

    def _update_table(self, customers: List[Any]) -> None:
        self.table.setRowCount(len(customers))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Full Name", "Email", "Score"])
        
        for i, c in enumerate(customers):
            self.table.setItem(i, 0, QTableWidgetItem(str(c.full_name)))
            self.table.setItem(i, 1, QTableWidgetItem(str(c.email)))
            score_item: QTableWidgetItem = QTableWidgetItem(str(c.credit_score))
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, score_item)

    def clear_kpi(self) -> None:
        while (item := self.kpi_layout.takeAt(0)) is not None:
            if widget := item.widget():
                widget.deleteLater()