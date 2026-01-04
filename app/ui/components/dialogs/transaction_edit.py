from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLineEdit, QFormLayout,
    QDateTimeEdit, QLabel, QPushButton, QMessageBox, QDialog, 
    QDoubleSpinBox
)

from PyQt6.QtCore import Qt, QDateTime

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from app.ui.styles import StyleSheet, DarkPalette

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

        labels: List[Tuple[str, QWidget]] = [
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
            f"""
            background-color: #7f8c8d; 
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