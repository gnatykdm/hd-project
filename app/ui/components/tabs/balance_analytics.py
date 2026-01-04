from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QComboBox, QLineEdit, QFormLayout,
    QStackedWidget, QTableWidget, QTableWidgetItem, QToolTip, QDateEdit, QDateTimeEdit,
    QFrame, QLabel, QCheckBox, QHeaderView, QPushButton, QMessageBox, QDialog, QDoubleSpinBox
)

from PyQt6.QtCharts import (
    QChartView, QChart, QLineSeries, QDateTimeAxis, QValueAxis
)

from PyQt6.QtGui import QPainter, QCursor, QPen
from PyQt6.QtCore import QTimer, Qt, QDate, QDateTime, QPointF

import numpy as np
from numpy.typing import NDArray
from datetime import datetime

from app.ui.styles import StyleSheet, DarkPalette
from app.ui.components.cards.metric import MetricCard

class BalanceAnalyticsTab(QWidget):
    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        
        self.kpi_layout: QHBoxLayout
        self.display_stack: QStackedWidget
        self.chart_view: QChartView
        self.table: QTableWidget
        self.btn_show_chart: QPushButton
        self.btn_show_table: QPushButton
        self.account_id: QLineEdit
        self.start_date: QDateEdit
        self.end_date: QDateEdit
        self.show_trend: QCheckBox
        self.run_btn: QPushButton
        
        self.init_ui()
        QTimer.singleShot(150, self.load_data)
    
    def init_ui(self) -> None:
        main_layout: QHBoxLayout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        left_container: QVBoxLayout = QVBoxLayout()
        
        self.kpi_layout = QHBoxLayout()
        left_container.addLayout(self.kpi_layout)
        
        self.display_stack = QStackedWidget()
        self._setup_views()
        left_container.addWidget(self.display_stack)
        
        main_layout.addLayout(left_container, stretch=3)
        
        sidebar: QFrame = self._create_sidebar()
        main_layout.addWidget(sidebar)

    def _setup_views(self) -> None:
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setMouseTracking(True)
        self.chart_view.setStyleSheet(f"""
            background-color: {DarkPalette.BG_MEDIUM.name()};
            border: 1px solid {DarkPalette.BORDER.name()};
            border-radius: 15px;
        """)
        
        self.table = QTableWidget()
        self.table.setStyleSheet(StyleSheet.TABLE)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Date", "Ending Balance"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.display_stack.addWidget(self.chart_view)
        self.display_stack.addWidget(self.table)

    def _create_sidebar(self) -> QFrame:
        sidebar: QFrame = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet(
            f"""background: {DarkPalette.BG_LIGHT.name()}; 
            border-radius: 20px; 
            border: 1px solid #333;
            """
        )
        layout: QVBoxLayout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 25, 20, 25)
        
        layout.addWidget(self._create_section_title("DISPLAY MODE"))
        view_nav: QHBoxLayout = QHBoxLayout()
        self.btn_show_chart = self._create_nav_btn("Graph", True, 0)
        self.btn_show_table = self._create_nav_btn("Table", False, 1)
        view_nav.addWidget(self.btn_show_chart)
        view_nav.addWidget(self.btn_show_table)
        layout.addLayout(view_nav)
        
        layout.addSpacing(20)
        layout.addWidget(self._create_section_title("TIME SERIES FILTERS"))
        
        layout.addWidget(QLabel("ACCOUNT ID"))
        self.account_id = QLineEdit("1")
        self.account_id.setStyleSheet(StyleSheet.LINE_EDIT)
        layout.addWidget(self.account_id)
        
        layout.addWidget(QLabel("START DATE"))
        self.start_date = QDateEdit(QDate.currentDate().addDays(-90))
        self.start_date.setCalendarPopup(True)
        layout.addWidget(self.start_date)
        
        layout.addWidget(QLabel("END DATE"))
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        layout.addWidget(self.end_date)
        
        layout.addSpacing(10)
        self.show_trend = QCheckBox("Apply Smoothing (Trend)")
        self.show_trend.setChecked(True)
        layout.addWidget(self.show_trend)
        
        layout.addStretch()
        
        self.run_btn = QPushButton("ANALYZE BALANCE")
        self.run_btn.setFixedHeight(50)
        self.run_btn.setStyleSheet(
            f"""background: {DarkPalette.ACCENT_BLUE.name()}; 
            color: white; 
            font-weight: bold; 
            border-radius: 12px;"""
        )
        self.run_btn.clicked.connect(self.load_data)
        layout.addWidget(self.run_btn)
        return sidebar

    def _create_nav_btn(self, text: str, checked: bool, index: int) -> QPushButton:
        btn: QPushButton = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedHeight(35)
        btn.setStyleSheet(StyleSheet.BUTTON)
        btn.clicked.connect(lambda: self._toggle_view(index))
        return btn

    def _toggle_view(self, index: int) -> None:
        self.display_stack.setCurrentIndex(index)
        self.btn_show_chart.setChecked(index == 0)
        self.btn_show_table.setChecked(index == 1)

    def _create_section_title(self, text: str) -> QLabel:
        lbl: QLabel = QLabel(text)
        lbl.setStyleSheet(
            f"""color: {DarkPalette.ACCENT_BLUE.name()}; 
            font-weight: 800; 
            font-size: 8pt; 
            letter-spacing: 1px;
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
            acc_id_text: str = self.account_id.text().strip()
            if not acc_id_text: 
                return
            
            acc_id: int = int(acc_id_text)
            start: Any = self.start_date.date().toPyDate()
            end: Any = self.end_date.date().toPyDate()
            
            balances: List[Any] = self.services['daily_balance'].get_by_date_range(acc_id, start, end)
            
            if not balances:
                self.chart_view.setChart(QChart())
                self.table.setRowCount(0)
                return

            dates_ts: List[float] = []
            vals: List[float] = []
            for b in balances:
                dt: datetime = datetime.combine(b.balance_date, datetime.min.time())
                dates_ts.append(dt.timestamp() * 1000)
                vals.append(float(b.ending_balance))

            self._fill_kpi(vals)

            self._fill_chart(dates_ts, vals)

            self.table.setRowCount(len(balances))
            for i, b in enumerate(balances):
                self.table.setItem(i, 0, QTableWidgetItem(str(b.balance_date)))
                self.table.setItem(i, 1, QTableWidgetItem(f"${b.ending_balance:,.2f}"))

        except Exception as e:
            QMessageBox.warning(self, "Data Error", f"Could not analyze data: {str(e)}")

    def _fill_kpi(self, vals: List[float]) -> None:
        mean_val: float = float(np.mean(vals))
        growth: float = ((vals[-1] - vals[0]) / vals[0] * 100) if vals[0] != 0 else 0.0
        
        self.kpi_layout.addWidget(MetricCard("Avg Balance", f"${mean_val:,.0f}", "Period Mean"))
        self.kpi_layout.addWidget(
            MetricCard(
                "Net Growth", 
                f"{growth:+.1f}%", 
                "Start vs End", 
                DarkPalette.ACCENT_GREEN if growth >= 0 else DarkPalette.ACCENT_ORANGE
            )
        )
        self.kpi_layout.addWidget(MetricCard("Peak", f"${max(vals):,.0f}", "Highest Point", DarkPalette.ACCENT_BLUE))
        self.kpi_layout.addStretch()

    def _fill_chart(self, dates_ts: List[float], vals: List[float]) -> None:
        chart: QChart = QChart()
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundVisible(False)
        
        main_series: QLineSeries = QLineSeries()
        main_series.setName("Actual Balance")
        pen: QPen = QPen(DarkPalette.ACCENT_BLUE)
        pen.setWidth(3)
        main_series.setPen(pen)
        main_series.setPointsVisible(True)

        for ts, val in zip(dates_ts, vals):
            main_series.append(ts, val)
        
        chart.addSeries(main_series)

        main_series.hovered.connect(self._handle_point_hover)

        trend_active: bool = self.show_trend.isChecked() and len(dates_ts) > 1
        trend_series: Optional[QLineSeries] = None
        
        if trend_active:
            trend_series = QLineSeries()
            trend_series.setName("Trend")
            t_pen: QPen = QPen(DarkPalette.ACCENT_GREEN)
            t_pen.setWidth(2)
            t_pen.setStyle(Qt.PenStyle.DashLine)
            trend_series.setPen(t_pen)

            x: NDArray[np.float_] = np.array(range(len(dates_ts)))
            y: NDArray[np.float_] = np.array(vals)
            coeffs: NDArray[np.float_] = np.polyfit(x, y, 1)
            m: float = float(coeffs[0])
            b_coeff: float = float(coeffs[1])
            
            for i in range(len(dates_ts)):
                trend_series.append(dates_ts[i], m * i + b_coeff)
            chart.addSeries(trend_series)

        axis_x: QDateTimeAxis = QDateTimeAxis()
        axis_x.setFormat("dd MMM")
        axis_x.setTickCount(min(len(dates_ts), 10))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        main_series.attachAxis(axis_x)
        if trend_active and trend_series: 
            trend_series.attachAxis(axis_x)

        axis_y: QValueAxis = QValueAxis()
        axis_y.setLabelFormat("$%.0f")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        main_series.attachAxis(axis_y)
        if trend_active and trend_series: 
            trend_series.attachAxis(axis_y)

        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.chart_view.setChart(chart)

    def _handle_point_hover(self, point: QPointF, state: bool) -> None:
        if state:
            dt: str = datetime.fromtimestamp(point.x() / 1000).strftime('%d %b %Y')
            QToolTip.showText(QCursor.pos(), f"<b>Date: {dt}</b><br>Balance: ${point.y():,.2f}")
        else:
            QToolTip.hideText()

class TransactionEditDialog(QDialog):
    def __init__(
        self, 
        services: Dict[str, Any], 
        account_id: Optional[int] = None, 
        transaction: Optional[Any] = None, 
        parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        self.account_id: Optional[int] = account_id
        self.transaction: Optional[Any] = transaction
        
        self.amount_input: QDoubleSpinBox
        self.category_input: QComboBox
        self.date_input: QDateTimeEdit
        self.merchant_input: QLineEdit
        self.btn_save: QPushButton
        
        mode_title: str = "Edit Transaction" if transaction else "New Transaction"
        self.setWindowTitle(mode_title)
        self.setFixedWidth(400)
        self.setStyleSheet(
            f"""
            background-color: {DarkPalette.BG_MEDIUM.name()}; 
            color: white;
            """
        )
        
        self.init_ui()
        if self.transaction:
            self.load_data()

    def init_ui(self) -> None:
        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setSpacing(15)

        form: QFormLayout = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(-9999999.0, 9999999.0)
        self.amount_input.setPrefix("$ ")
        self.amount_input.setDecimals(2)
        self.amount_input.setStyleSheet(StyleSheet.LINE_EDIT)
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(["Salary", "Transfer", "Food", "Rent", "Shopping", "Entertainment", "Health"])
        self.category_input.setStyleSheet(StyleSheet.COMBO_BOX)
        
        self.date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet(StyleSheet.LINE_EDIT)

        self.merchant_input = QLineEdit()
        self.merchant_input.setPlaceholderText("Optional: Amazon, Starbucks...")
        self.merchant_input.setStyleSheet(StyleSheet.LINE_EDIT)

        labels: List[tuple[str, QWidget]] = [
            ("Amount:", self.amount_input), 
            ("Category:", self.category_input),
            ("Timestamp:", self.date_input),
            ("Merchant:", self.merchant_input)
        ]
        
        for text, widget in labels:
            lbl: QLabel = QLabel(text)
            lbl.setStyleSheet(f"color: {DarkPalette.ACCENT_BLUE.name()}; font-weight: bold;")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        btn_layout: QHBoxLayout = QHBoxLayout()
        self.btn_save = QPushButton("SAVE")
        self.btn_save.setStyleSheet(
            f"""
            background-color: {DarkPalette.ACCENT_GREEN.name()}; 
            color: white; 
            font-weight: bold; 
            padding: 8px; 
            border-radius: 5px;
            """
        )
        self.btn_save.clicked.connect(self.save_data)
        
        btn_cancel: QPushButton = QPushButton("CANCEL")
        btn_cancel.setStyleSheet(
            f"""background-color: #7f8c8d; 
            color: white; 
            font-weight: bold; 
            padding: 8px; 
            border-radius: 5px;
            """
        )
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def load_data(self) -> None:
        if not self.transaction:
            return
            
        self.amount_input.setValue(float(self.transaction.amount))
        self.category_input.setCurrentText(self.transaction.category)
        self.merchant_input.setText(getattr(self.transaction, 'merchant_name', ""))
        py_dt: datetime = self.transaction.timestamp
        self.date_input.setDateTime(QDateTime(py_dt.year, py_dt.month, py_dt.day, py_dt.hour, py_dt.minute))

    def save_data(self) -> None:
        data: Dict[str, Any] = {
            "amount": self.amount_input.value(),
            "category": self.category_input.currentText(),
            "timestamp": self.date_input.dateTime().toPyDateTime(),
            "merchant_name": self.merchant_input.text()
        }

        try:
            if self.transaction:
                self.services['transaction'].update(self.transaction.id, **data)
                
                for key, value in data.items():
                    setattr(self.transaction, key, value)
            else:
                data["account_id"] = self.account_id
                new_tx: Any = self.services['transaction'].create(**data)
                
                parent_widget: Optional[QWidget] = self.parent()
                if parent_widget and hasattr(parent_widget, 'account'):
                    parent_widget.account.transactions.append(new_tx)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not save: {str(e)}")