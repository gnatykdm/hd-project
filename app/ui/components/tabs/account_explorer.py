from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QStyle, QScrollArea, QMenu,
    QFrame, QLabel, QPushButton, QMessageBox, QHeaderView
)

from PyQt6.QtGui import QColor, QCursor, QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRegularExpression

from typing import Dict, List, Any, Optional

from app.ui.styles import StyleSheet, DarkPalette
from app.ui.components.dialogs.account_details import AccountDetailsDialog
from app.ui.components.dialogs.transaction_edit import TransactionEditDialog

class AccountExplorerTab(QWidget):
    account_selected: pyqtSignal = pyqtSignal(int)

    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        
        self.search_panel: QFrame
        self.results_area: QScrollArea
        self.results_content: QWidget
        self.results_layout: QVBoxLayout
        self.search_type: QComboBox
        self.search_query: QLineEdit
        
        self.init_ui()
    
    def init_ui(self) -> None:
        main_layout: QVBoxLayout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        self.search_panel = self._create_search_panel()
        main_layout.addWidget(self.search_panel)
        
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.results_content = QWidget()
        self.results_layout = QVBoxLayout(self.results_content)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(15)
        self.results_layout.addStretch() 
        
        self.results_area.setWidget(self.results_content)
        main_layout.addWidget(self.results_area)

    def _create_search_panel(self) -> QFrame:
        panel: QFrame = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{ 
                background-color: {DarkPalette.BG_LIGHT.name()}; 
                border-radius: 15px; 
                border: 1px solid {DarkPalette.BORDER.name()}; 
            }}
        """)
        layout: QHBoxLayout = QHBoxLayout(panel)
        
        label_search: QLabel = QLabel("SEARCH BY")
        label_search.setStyleSheet(
            f"""
            color: {DarkPalette.ACCENT_BLUE.name()}; 
            font-weight: 800; 
            font-size: 8pt; 
            border: none;
            """
        )
        layout.addWidget(label_search)
        
        self.search_type = QComboBox()
        self.search_type.addItems(["Account ID", "Full Name", "Customer Email", "Account Number"])
        self.search_type.setFixedWidth(150)
        self.search_type.setStyleSheet(StyleSheet.COMBO_BOX)
        layout.addWidget(self.search_type)
        
        self.search_query = QLineEdit()
        self.search_query.setPlaceholderText("Enter identification details...")
        self.search_query.setStyleSheet(StyleSheet.LINE_EDIT)
        self.search_query.returnPressed.connect(self.perform_search)
        layout.addWidget(self.search_query)

        self.search_type.currentTextChanged.connect(self._update_search_validator)
        
        search_btn: QPushButton = QPushButton(" SEARCH")
        search_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        search_btn.setStyleSheet(StyleSheet.BUTTON)
        search_btn.clicked.connect(self.perform_search)
        layout.addWidget(search_btn)
        
        return panel
    
    def _update_search_validator(self) -> None:
        t = self.search_type.currentText()
        self.search_query.clear()

        if t == "Account ID":
            self.search_query.setValidator(QIntValidator(1, 10**9))

        elif t == "Account Number":
            self.search_query.setValidator(
                QRegularExpressionValidator(QRegularExpression(r"\d{8,20}"))
            )

        elif t == "Customer Email":
            self.search_query.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression(r"^[\w\.-]+@[\w\.-]+\.\w+$")
                )
            )

        elif t == "Full Name":
            self.search_query.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression(r"[A-Za-z\s\-]{2,50}")
                )
            )

        else:
            self.search_query.setValidator(None)

    def perform_search(self) -> None:
        try:
            self._clear_layout(self.results_layout)
            query: str = self.search_query.text().strip()
            if not query: 
                return

            if not self.search_query.hasAcceptableInput():
                QMessageBox.warning(
                    self,
                    "Invalid input",
                    f"Invalid value for '{self.search_type.currentText()}'"
                )
                return

            search_type: str = self.search_type.currentText()
            results: List[Any] = []

            if search_type == "Account Number":
                acc: Optional[Any] = self.services['account'].get_acc_by_number(query)
                if acc: 
                    results = [acc]
            elif search_type == "Account ID":
                if query.isdigit():
                    acc = self.services['account'].get_acc_by_id(int(query))
                    if acc: 
                        results = [acc]
            elif search_type == "Full Name":
                customers: List[Any] = self.services['customer'].get_all()
                target_custs: List[Any] = [c for c in customers if query.lower() in c.full_name.lower()]
                for c in target_custs:
                    results.extend(self.services['account'].get_accounts_by_customer(c.id))
            elif search_type == "Customer Email":
                customer: Optional[Any] = self.services['customer'].get_by_email(query)
                if customer:
                    results = self.services['account'].get_accounts_by_customer(customer.id)

            if results:
                for acc in results:
                    self.display_account_card(acc)
            else:
                self._show_empty_state()

            self.results_layout.addStretch()
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Details: {str(e)}")

    def display_account_card(self, acc: Any) -> None:
        card: QFrame = QFrame()
        card.setObjectName("AccountCard")
        card.setStyleSheet(f"""
            QFrame#AccountCard {{
                background-color: {DarkPalette.BG_MEDIUM.name()};
                border: 1px solid {DarkPalette.BORDER.name()};
                border-radius: 20px;
            }}
            QFrame#AccountCard:hover {{
                border: 1px solid {DarkPalette.ACCENT_BLUE.name()};
                background-color: {DarkPalette.BG_LIGHT.name()};
            }}
        """)
        
        card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        card.customContextMenuRequested.connect(lambda pos: self._show_context_menu(pos, acc))
        
        layout: QVBoxLayout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)

        header: QHBoxLayout = QHBoxLayout()
        acc_info: QVBoxLayout = QVBoxLayout()
        acc_num: QLabel = QLabel(f"ACC: {acc.account_number}")
        acc_num.setStyleSheet(
            """
            font-size: 16pt; 
            font-weight: bold; 
            color: white; 
            border: none;
            """
        )
        acc_type: QLabel = QLabel(f"{acc.account_type.upper()} ACCOUNT")
        acc_type.setStyleSheet(
            f"""
            color: {DarkPalette.ACCENT_BLUE.name()}; 
            font-size: 8pt; 
            font-weight: bold; 
            border: none;
            """
        )
        acc_info.addWidget(acc_num)
        acc_info.addWidget(acc_type)
        
        status_tag: QLabel = QLabel("ACTIVE" if acc.is_active else "INACTIVE")
        status_color: str = "#2ecc71" if acc.is_active else "#e74c3c"
        status_tag.setStyleSheet(
            f"""
            background: {status_color}22;
            color: {status_color};
            border: 1px solid {status_color};
            border-radius: 8px; 
            padding: 5px 12px; 
            font-weight: bold; 
            font-size: 7pt;
            """
        )
        header.addLayout(acc_info)
        header.addStretch()
        header.addWidget(status_tag, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

        grid: QGridLayout = QGridLayout()
        grid.setContentsMargins(0, 15, 0, 15)
        self._add_info_item(grid, 0, 0, "CLIENT NAME", acc.customer.full_name)
        self._add_info_item(grid, 0, 1, "SEGMENT", acc.customer.customer_segment or "Standard")
        self._add_info_item(grid, 1, 0, "CREDIT SCORE", str(acc.customer.credit_score))
        self._add_info_item(grid, 1, 1, "PRIMARY BRANCH", acc.branch.branch_name)
        layout.addLayout(grid)

        trans_table: QTableWidget = self._create_recent_transactions_table(acc)
        layout.addWidget(trans_table)

        footer: QHBoxLayout = QHBoxLayout()
        try:
            latest: Optional[Any] = self.services['daily_balance'].get_latest_balance(acc.id)
            balance_str: str = f"${latest.ending_balance:,.2f}" if latest else "$0.00"
        except: 
            balance_str = "$ ---"

        bal_layout: QVBoxLayout = QVBoxLayout()
        bal_label: QLabel = QLabel("TOTAL BALANCE")
        bal_label.setStyleSheet(
            f"""
            color: {DarkPalette.TEXT_SECONDARY.name()}; 
            font-size: 7pt; 
            font-weight: 800; 
            border: none;
            """
        )
        bal_val: QLabel = QLabel(balance_str)
        bal_val.setStyleSheet(
            f"""
            color: {DarkPalette.ACCENT_GREEN.name()}; 
            font-size: 18pt; 
            font-weight: 800; 
            border: none;
            """
        )
        bal_layout.addWidget(bal_label)
        bal_layout.addWidget(bal_val)
        
        view_analytics_btn: QPushButton = QPushButton(" VIEW ANALYTICS")
        view_analytics_btn.setFixedWidth(160)
        view_analytics_btn.setFixedHeight(40)
        view_analytics_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_analytics_btn.setStyleSheet(StyleSheet.BUTTON)
        view_analytics_btn.clicked.connect(lambda: self._open_account_details(acc))

        footer.addLayout(bal_layout)
        footer.addStretch()
        footer.addWidget(view_analytics_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(footer)

        self.results_layout.insertWidget(0, card)

    def _show_context_menu(self, pos: QPoint, acc: Any) -> None:
        menu: QMenu = QMenu(self)
        menu.setStyleSheet(StyleSheet.CONTEXT_MENU)
        
        edit_act = menu.addAction(" ✎ Edit Account")
        add_tx_act = menu.addAction(" ➕ Add Transaction")
        menu.addSeparator()
        del_act = menu.addAction(" 🗑 Delete Account")
        
        action = menu.exec(QCursor.pos())
        
        if action == edit_act:
            self._edit_account(acc)
        elif action == add_tx_act:
            self._add_transaction(acc)
        elif action == del_act:
            self._delete_account(acc)

    def _create_new_account(self) -> None:
        QMessageBox.information(self, "Action", "Open Account Creation Dialog here")

    def _edit_account(self, acc: Any) -> None:
        QMessageBox.information(self, "Action", f"Editing account: {acc.account_number}")

    def _add_transaction(self, acc: Any) -> None:
        try:
            dialog: TransactionEditDialog = TransactionEditDialog(
                self.services, 
                account_id=acc.id, 
                parent=self
            )
            if dialog.exec():
                self.perform_search()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open transaction dialog: {e}")

    def _delete_account(self, acc: Any) -> None:
        confirm: QMessageBox.StandardButton = QMessageBox.question(
            self, 
            "Confirm Delete",
            f"Are you sure you want to delete account {acc.account_number}?\nAll history will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            if self.services['account'].delete(acc.id):
                self.perform_search()

    def _open_account_details(self, acc: Any) -> None:
        dialog: AccountDetailsDialog = AccountDetailsDialog(acc, self.services, self)
        dialog.exec()
        self.perform_search()
        self.account_selected.emit(acc.id)

    def _create_recent_transactions_table(self, acc: Any) -> QTableWidget:
        table: QTableWidget = QTableWidget()
        table.setFixedHeight(130)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Date", "Category", "Amount"])
        table.setStyleSheet(StyleSheet.TABLE)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        
        try:
            recent_tx: List[Any] = sorted(acc.transactions, key=lambda x: x.timestamp, reverse=True)[:3]
            table.setRowCount(len(recent_tx))
            for i, tx in enumerate(recent_tx):
                table.setItem(i, 0, QTableWidgetItem(tx.timestamp.strftime("%d %b %Y")))
                table.setItem(i, 1, QTableWidgetItem(tx.category))
                amt_item: QTableWidgetItem = QTableWidgetItem(f"${tx.amount:,.2f}")
                amt_item.setForeground(QColor("#e74c3c") if tx.amount < 0 else QColor("#2ecc71"))
                amt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(i, 2, amt_item)
        except:
            table.setRowCount(0)
        return table

    def _add_info_item(
        self, 
        grid: QGridLayout, 
        row: int, 
        col: int, 
        label: str, 
        value: str
    ) -> None:
        box: QVBoxLayout = QVBoxLayout()
        l: QLabel = QLabel(label)
        l.setStyleSheet(
            f"""
            color: {DarkPalette.ACCENT_BLUE.name()}; 
            font-size: 7pt; 
            font-weight: 800; 
            border: none;
            """
        )
        v: QLabel = QLabel(str(value))
        v.setStyleSheet(
            """
            color: white; 
            font-size: 10pt; 
            border: none; 
            font-weight: 500;
            """
        )
        box.addWidget(l)
        box.addWidget(v)
        grid.addLayout(box, row, col)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def _show_empty_state(self) -> None:
        msg: QLabel = QLabel("No accounts found matching your criteria.")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet(
            f"""color: {DarkPalette.TEXT_SECONDARY.name()}; 
            font-style: italic; 
            margin-top: 50px; 
            font-size: 11pt;
            """
        )
        self.results_layout.insertWidget(0, msg)