from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QSplitter,
    QFrame, QLabel, QPushButton, QMessageBox, QHeaderView
)

from PyQt6.QtCharts import (
    QChartView, QChart, QBarSeries, QBarSet, QLineSeries
)

from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt

import numpy as np
import pandas as pd
from datetime import date
from typing import Dict, List, Any, Optional, Tuple

from app.ui.styles import StyleSheet, DarkPalette

class AdvancedDataExplorerTab(QWidget):
    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        
        self.source_combo: QComboBox
        self.search_input: QLineEdit
        self.help_box: QFrame
        self.help_label: QLabel
        self.sort_combo: QComboBox
        self.sort_order: QComboBox
        self.chart_type_combo: QComboBox
        self.execute_btn: QPushButton
        self.splitter: QSplitter
        self.chart_view: QChartView
        self.table: QTableWidget
        
        self.init_ui()
    
    def init_ui(self) -> None:
        main_layout: QHBoxLayout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        sidebar: QFrame = QFrame()
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet(f"""
            QFrame {{ 
                background: {DarkPalette.BG_LIGHT.name()}; 
                border-radius: 20px; 
                border: 1px solid #333; 
            }}
            QLabel {{ border: none; color: {DarkPalette.TEXT_PRIMARY.name()}; font-weight: bold; }}
        """)
        side_layout: QVBoxLayout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 25, 20, 25)

        side_layout.addWidget(self._create_header("DATABASE TABLE"))
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Customers", "Accounts", "Transactions", "Branches", "Balances"])
        self.source_combo.setStyleSheet(StyleSheet.COMBO_BOX)
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        side_layout.addWidget(self.source_combo)

        side_layout.addSpacing(15)

        side_layout.addWidget(self._create_header("QUERY FILTER"))
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet(StyleSheet.LINE_EDIT)
        side_layout.addWidget(self.search_input)
        
        self.help_box = QFrame()
        self.help_box.setStyleSheet(
            f"""
            background: {DarkPalette.BG_MEDIUM.name()}; 
            border-radius: 10px; 
            border: none;
        """)
        help_layout: QVBoxLayout = QVBoxLayout(self.help_box)
        self.help_label = QLabel("")
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet(
            """
            color: #888; 
            font-size: 8pt; 
            font-style: italic; 
            font-weight: normal;
            """
        )
        help_layout.addWidget(self.help_label)
        side_layout.addWidget(self.help_box)

        side_layout.addSpacing(15)

        side_layout.addWidget(self._create_header("SORTING"))
        self.sort_combo = QComboBox()
        self.sort_combo.setStyleSheet(StyleSheet.COMBO_BOX)
        side_layout.addWidget(self.sort_combo)
        
        self.sort_order = QComboBox()
        self.sort_order.addItems(["Descending", "Ascending"])
        self.sort_order.setStyleSheet(StyleSheet.COMBO_BOX)
        side_layout.addWidget(self.sort_order)

        side_layout.addSpacing(15)

        side_layout.addWidget(self._create_header("VISUALIZATION"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["📊 Bar Chart", "📈 Line Chart", "🚫 Table Only"])
        self.chart_type_combo.setStyleSheet(StyleSheet.COMBO_BOX)
        side_layout.addWidget(self.chart_type_combo)

        side_layout.addStretch()

        self.execute_btn = QPushButton("🚀 RUN ANALYSIS")
        self.execute_btn.setFixedHeight(50)
        self.execute_btn.setStyleSheet(f"""
            QPushButton {{
                background: {DarkPalette.ACCENT_BLUE.name()}; 
                color: white; 
                font-weight: bold; 
                border-radius: 12px;
                font-size: 10pt;
            }}
            QPushButton:hover {{ background: {DarkPalette.ACCENT_BLUE.lighter(120).name()}; }}
        """)
        self.execute_btn.clicked.connect(self.run_query)
        side_layout.addWidget(self.execute_btn)

        content_layout: QVBoxLayout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Orientation.Vertical)

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet(
            f"""
            background: {DarkPalette.BG_MEDIUM.name()}; 
            border: 1px solid #333; 
            border-radius: 15px;
            """
        )
        self.chart_view.hide()

        self.table = QTableWidget()
        self.table.setStyleSheet(StyleSheet.TABLE)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.splitter.addWidget(self.chart_view)
        self.splitter.addWidget(self.table)
        self.splitter.setStretchFactor(1, 2)

        content_layout.addWidget(self.splitter)
        
        main_layout.addWidget(sidebar)
        main_layout.addLayout(content_layout, stretch=1)
        
        self.on_source_changed(self.source_combo.currentText())

    def _create_header(self, text: str) -> QLabel:
        lbl: QLabel = QLabel(text)
        lbl.setStyleSheet(f"color: {DarkPalette.ACCENT_BLUE.name()}; font-weight: 800; font-size: 8pt; letter-spacing: 1.2px;")
        return lbl

    def on_source_changed(self, source: str) -> None:
        configs: Dict[str, Tuple[str, List[str]]] = {
            "Customers": ("Filter by name or segment (e.g. VIP)", ["credit_score", "full_name", "created_at"]),
            "Accounts": ("Filter by type (SAVINGS/CHECKING)", ["account_type", "is_active"]),
            "Transactions": ("Filter by category (Food, Rent...)", ["amount", "timestamp", "category"]),
            "Branches": ("Filter by region (North, South...)", ["branch_name", "region"]),
            "Balances": ("Enter Account ID to see history", ["balance_date", "ending_balance"])
        }
        
        hint: str
        sort_fields: List[str]
        hint, sort_fields = configs.get(source, ("", []))
        self.help_label.setText(f"💡 {hint}")
        self.search_input.setPlaceholderText(f"Search in {source}...")
        self.sort_combo.clear()
        self.sort_combo.addItems(sort_fields)

    def run_query(self) -> None:
        try:
            source: str = self.source_combo.currentText()
            search_text: str = self.search_input.text().strip().lower()
            
            data: List[Dict[str, Any]] = self._get_raw_data(source)
            if not data:
                QMessageBox.information(self, "Data Explorer", "No records found in database.")
                return

            df: pd.DataFrame = pd.DataFrame(data)

            if search_text:
                mask: pd.Series = df.apply(
                    lambda row: row.astype(str).str.lower().str.contains(search_text).any(), 
                    axis=1
                )
                df = df[mask]

            sort_col: str = self.sort_combo.currentText()
            is_asc: bool = self.sort_order.currentText() == "Ascending"
            if sort_col in df.columns:
                df = df.sort_values(by=sort_col, ascending=is_asc)

            if df.empty:
                QMessageBox.warning(self, "No Results", "No data matches your search criteria.")
                return

            self.display_results(df)
            self.update_chart(df)

        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Failed to process query: {str(e)}")

    def _get_raw_data(self, source: str) -> List[Dict[str, Any]]:
        if source == "Customers":
            return [
                {
                    "id": c.id, 
                    "full_name": c.full_name, 
                    "credit_score": c.credit_score, 
                    "segment": c.customer_segment
                } 
                for c in self.services['customer'].get_all()
            ]
        
        elif source == "Accounts":
            return [
                {
                    "number": a.account_number, 
                    "type": a.account_type, 
                    "is_active": a.is_active
                } 
                for a in self.services['account'].get_all()
            ]
        
        elif source == "Transactions":
            return [
                {
                    "timestamp": t.timestamp.strftime("%Y-%m-%d"), 
                    "amount": t.amount, 
                    "category": t.category, 
                    "merchant": t.merchant_name
                } 
                for t in self.services['transaction'].get_all()
            ]
        
        elif source == "Branches":
            res: List[Dict[str, Any]] = self.services['branch'].get_branches_by_account_count(0)
            return [
                {
                    "branch_name": b['branch'].branch_name, 
                    "region": b['branch'].region, 
                    "accounts": b['account_count']
                } 
                for b in res
            ]
        
        elif source == "Balances":
            raw: List[Any] = self.services['daily_balance'].get_by_date_range(
                1, 
                date(2025, 1, 1), 
                date.today()
            )
            return [
                {
                    "balance_date": str(b.balance_date), 
                    "ending_balance": b.ending_balance
                } 
                for b in raw
            ]
        
        return []

    def display_results(self, df: pd.DataFrame) -> None:
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in df.columns])
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                val: Any = df.iloc[i][col]
                display_text: str
                if isinstance(val, (int, float)) and any(x in col for x in ['amount', 'balance', 'score']):
                    display_text = f"{val:,.0f}" if 'score' in col else f"${val:,.2f}"
                else:
                    display_text = str(val)
                
                item: QTableWidgetItem = QTableWidgetItem(display_text)
                if isinstance(val, (int, float)): 
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def update_chart(self, df: pd.DataFrame) -> None:
        chart_mode: str = self.chart_type_combo.currentText()
        if "No" in chart_mode:
            self.chart_view.hide()
            return

        self.chart_view.show()
        chart: QChart = QChart()
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundVisible(False)

        num_cols: pd.Index = df.select_dtypes(include=[np.number]).columns
        if num_cols.empty: 
            return
        
        y_axis_col: str = str(num_cols[0])
        x_axis_col: str = str(df.columns[0])

        if "Bar" in chart_mode:
            series: QBarSeries = QBarSeries()
            bar_set: QBarSet = QBarSet(y_axis_col.title())
            bar_set.setColor(QColor(DarkPalette.ACCENT_BLUE.name()))
            for v in df[y_axis_col].head(15): 
                bar_set.append(float(v))
            series.append(bar_set)
            chart.addSeries(series)
        else:
            line_series: QLineSeries = QLineSeries()
            pen: QPen = QPen(QColor(DarkPalette.ACCENT_GREEN.name()))
            pen.setWidth(3)
            line_series.setPen(pen)
            for i, v in enumerate(df[y_axis_col].head(50)): 
                line_series.append(i, float(v))
            chart.addSeries(line_series)

        chart.createDefaultAxes()
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        self.chart_view.setChart(chart)