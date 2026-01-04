from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QToolTip, QStyle,
    QFrame, QLabel, QPushButton, QMessageBox, QDialog, QHeaderView, QApplication
)

from PyQt6.QtGui import QColor, QCursor
from PyQt6.QtCore import Qt

from typing import Dict, List, Any, Optional, Tuple

from app.ui.styles import StyleSheet, DarkPalette
from app.ui.components.dialogs.transaction_edit import TransactionEditDialog

class AccountDetailsDialog(QDialog):
    def __init__(
        self, 
        account: Any, 
        services: Dict[str, Any], 
        parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.account: Any = account
        self.services: Dict[str, Any] = services
        
        self.tabs: QTabWidget
        self.search_tx: QLineEdit
        self.table: QTableWidget
        
        self.setWindowTitle(f"Account Management: {account.account_number}")
        self.setMinimumSize(950, 700)
        self.setStyleSheet(
            f"""
            background-color: {DarkPalette.BG_MEDIUM.name()};
            """
        )
        self.init_ui()

    def init_ui(self) -> None:
        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header: QFrame = QFrame()
        header.setStyleSheet(
            f"""
            background: {DarkPalette.BG_LIGHT.name()}; 
            border-radius: 12px; 
            border: 1px solid {DarkPalette.BORDER.name()};
            """
        )
        header_layout: QHBoxLayout = QHBoxLayout(header)
        
        info_text: str = f"{self.account.customer.full_name} | {self.account.account_number}"
        lbl_info: QLabel = QLabel(info_text)
        lbl_info.setStyleSheet("color: white; font-size: 11pt; font-weight: bold; border: none;")
        
        btn_copy: QPushButton = QPushButton(" Copy Info")
        btn_copy.setStyleSheet(StyleSheet.BUTTON)
        btn_copy.clicked.connect(self.copy_to_clipboard)
        
        header_layout.addWidget(lbl_info)
        header_layout.addStretch()
        header_layout.addWidget(btn_copy)
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(StyleSheet.TABLE)
        self.tabs.addTab(self._create_transactions_tab(), "Transactions & CRUD")
        self.tabs.addTab(self._create_info_tab(), "Full Profile")
        layout.addWidget(self.tabs)

        btn_close: QPushButton = QPushButton("CLOSE")
        btn_close.setFixedHeight(40)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"background: {DarkPalette.BG_LIGHT.name()}; color: white; border-radius: 8px; font-weight: bold;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def copy_to_clipboard(self) -> None:
        data: str = (
            f"Client: {self.account.customer.full_name}\n"
            f"Acc: {self.account.account_number}\n"
            f"Type: {self.account.account_type}\n"
            f"Branch: {self.account.branch.branch_name}"
        )
        QApplication.clipboard().setText(data)
        QToolTip.showText(QCursor.pos(), "✅ Copied to clipboard")

    def _create_transactions_tab(self) -> QWidget:
        widget: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(widget)

        ctrl_panel: QHBoxLayout = QHBoxLayout()
        btn_add: QPushButton = QPushButton(" + ADD TRANSACTION")
        btn_add.setFixedWidth(180)
        btn_add.setStyleSheet(f"background-color: {DarkPalette.ACCENT_GREEN.name()}; color: white; font-weight: bold; border-radius: 6px; padding: 5px;")
        btn_add.clicked.connect(self._add_transaction)
        
        self.search_tx = QLineEdit()
        self.search_tx.setPlaceholderText("Quick filter by category...")
        self.search_tx.setStyleSheet(StyleSheet.LINE_EDIT)
        self.search_tx.textChanged.connect(self.refresh_transactions)

        ctrl_panel.addWidget(btn_add)
        ctrl_panel.addSpacing(20)
        ctrl_panel.addWidget(self.search_tx)
        layout.addLayout(ctrl_panel)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Amount", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 110)
        self.table.setStyleSheet(StyleSheet.TABLE)
        
        layout.addWidget(self.table)
        self.refresh_transactions()
        
        return widget

    def refresh_transactions(self) -> None:
        query: str = self.search_tx.text().lower().strip()
        tx_list: List[Any] = getattr(self.account, 'transactions', []) or []
        
        filtered: List[Any] = sorted(
            [t for t in tx_list if query in (t.category or "").lower()],
            key=lambda x: x.timestamp, 
            reverse=True
        )

        self.table.setRowCount(len(filtered))
        for i, tx in enumerate(filtered):
            self.table.setItem(i, 0, QTableWidgetItem(str(tx.id)))
            self.table.setItem(i, 1, QTableWidgetItem(tx.timestamp.strftime("%Y-%m-%d")))
            self.table.setItem(i, 2, QTableWidgetItem(tx.category))
            
            amt: float = float(tx.amount or 0)
            amt_item: QTableWidgetItem = QTableWidgetItem(f"${amt:,.2f}")
            amt_item.setForeground(QColor("#2ecc71") if amt > 0 else QColor("#e74c3c"))
            amt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 3, amt_item)

            btn_container: QWidget = QWidget()
            btn_layout: QHBoxLayout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setSpacing(8)

            btn_edit: QPushButton = QPushButton()
            btn_edit.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
            btn_edit.setFixedSize(30, 25)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.clicked.connect(lambda chk, t=tx: self._edit_transaction(t))

            btn_del: QPushButton = QPushButton()
            btn_del.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
            btn_del.setFixedSize(30, 25)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.clicked.connect(lambda chk, t=tx: self._delete_transaction(t))

            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_del)
            self.table.setCellWidget(i, 4, btn_container)

    def _create_info_tab(self) -> QWidget:
        widget: QWidget = QWidget()
        grid: QGridLayout = QGridLayout(widget)
        grid.setSpacing(20)
        
        details: List[Tuple[str, str]] = [
            ("Customer ID", str(self.account.customer_id)),
            ("Email", self.account.customer.email),
            ("Credit Score", str(self.account.customer.credit_score)),
            ("Branch", self.account.branch.branch_name),
            ("Status", "Active" if self.account.is_active else "Inactive")
        ]
        
        for i, (label, value) in enumerate(details):
            lbl: QLabel = QLabel(label.upper())
            lbl.setStyleSheet(
                f"""
                color: {DarkPalette.ACCENT_BLUE.name()}; 
                font-size: 8pt; 
                font-weight: 800;
                """
            )
            val: QLabel = QLabel(str(value))
            val.setStyleSheet("color: white; font-size: 10pt;")
            grid.addWidget(lbl, i // 2, (i % 2) * 2)
            grid.addWidget(val, i // 2, (i % 2) * 2 + 1)
        
        grid.setRowStretch(grid.rowCount(), 1)
        return widget

    def _add_transaction(self) -> None:        
        dialog: TransactionEditDialog = TransactionEditDialog(
            services=self.services, 
            account_id=self.account.id, 
            parent=self
        )
        if dialog.exec():
            self.refresh_transactions()

    def _edit_transaction(self, tx: Any) -> None:        
        dialog: TransactionEditDialog = TransactionEditDialog(
            services=self.services, 
            transaction=tx, 
            parent=self
        )
        if dialog.exec():
            self.refresh_transactions()

    def _delete_transaction(self, tx: Any) -> None:
        reply: QMessageBox.StandardButton = QMessageBox.question(
            self, 
            "Confirm", 
            f"Delete transaction #{tx.id}?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.services['transaction'].delete(tx.id)
                if tx in self.account.transactions:
                    self.account.transactions.remove(tx)
                self.refresh_transactions()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))