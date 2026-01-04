from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QFrame, QLabel, QPushButton,
    QListWidget, QLineEdit, QComboBox, QMessageBox
)
from PyQt6.QtGui import QValidator, QIntValidator, QDoubleValidator
from PyQt6.QtCore import QTimer, Qt

from typing import Dict, List, Any, Optional, Callable, Tuple

from app.ui.styles import StyleSheet, DarkPalette

class DataManagementTab(QWidget):    
    def __init__(self, services: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.services: Dict[str, Any] = services
        
        self.menu_list: QListWidget
        self.stack: QStackedWidget
        self.status_bar: QFrame
        self.status_label: QLabel
        self.del_type: QComboBox
        self.del_id: QLineEdit
        
        self.init_ui()

    def init_ui(self) -> None:
        main_layout: QHBoxLayout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(220)
        self.menu_list.setStyleSheet(f"""
            QListWidget {{
                background: {DarkPalette.BG_LIGHT.name()};
                border-radius: 15px;
                border: 1px solid {DarkPalette.BORDER.name()};
                padding: 10px;
                outline: none;
            }}
            QListWidget::item {{
                height: 50px;
                color: #bbb;
                border-radius: 8px;
                margin-bottom: 5px;
                padding-left: 10px;
            }}
            QListWidget::item:selected {{
                background: {DarkPalette.ACCENT_BLUE.name()}33;
                color: {DarkPalette.ACCENT_BLUE.name()};
                font-weight: bold;
            }}
        """)
        self.menu_list.addItems([
            "👤 New Customer",
            "💳 Open Account",
            "💸 Record Transaction",
            "🛠 Maintenance"
        ])
        self.menu_list.currentRowChanged.connect(self.switch_mode)
        main_layout.addWidget(self.menu_list)

        right_container: QVBoxLayout = QVBoxLayout()
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {DarkPalette.BG_MEDIUM.name()}; border-radius: 15px;")
        
        self.stack.addWidget(self._create_customer_page())
        self.stack.addWidget(self._create_account_page())
        self.stack.addWidget(self._create_tx_page())
        self.stack.addWidget(self._create_maint_page())

        right_container.addWidget(self.stack)

        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(45)
        self.status_bar.setStyleSheet(
            f"""
            background: {DarkPalette.BG_LIGHT.name()}; 
            border-radius: 10px;
            """
        )
        status_layout: QHBoxLayout = QHBoxLayout(self.status_bar)
        self.status_label = QLabel("Ready for data operations...")
        self.status_label.setStyleSheet(
            """
            color: #888; 
            font-size: 9pt; 
            margin-left: 10px;
            """
        )
        status_layout.addWidget(self.status_label)
        right_container.addWidget(self.status_bar)

        main_layout.addLayout(right_container, 1)
        self.menu_list.setCurrentRow(0)

    def switch_mode(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        item = self.menu_list.item(index)
        if item:
            self.status_label.setText(f"Switching to mode: {item.text()}")

    def _create_customer_page(self) -> QWidget:
        """Create the customer registration page."""
        return self._build_base_page("REGISTER CUSTOMER", [
            ("Full Name", "txt_name", None),
            ("Email Address", "txt_email", None),
            ("Initial Credit Score", "num_score", QIntValidator(300, 850))
        ], "Create Record", self.handle_create_customer)

    def _create_account_page(self) -> QWidget:
        """Create the account opening page."""
        return self._build_base_page("OPEN NEW ACCOUNT", [
            ("Target Customer ID", "num_cust_id", QIntValidator()),
            ("Branch Code", "num_branch_id", QIntValidator()),
            ("Account Number (IBAN)", "txt_acc_num", None)
        ], "Activate Account", self.handle_create_account)

    def _create_tx_page(self) -> QWidget:
        """Create the transaction recording page."""
        return self._build_base_page("NEW TRANSACTION", [
            ("Source Account ID", "num_acc_id_tx", QIntValidator()),
            ("Transaction Amount", "num_amount", QDoubleValidator()),
            ("Category (Food, Rent...)", "txt_cat", None)
        ], "Post Transaction", self.handle_post_transaction)

    def _create_maint_page(self) -> QWidget:
        page: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(page)
        layout.setContentsMargins(60, 60, 60, 60)
        
        title: QLabel = QLabel("MAINTENANCE OPERATIONS")
        title.setStyleSheet(
            """
            font-size: 18pt; 
            font-weight: 800; 
            color: #e74c3c; 
            margin-bottom: 20px;
            """
        )
        layout.addWidget(title)
        
        layout.addWidget(QLabel("SELECT ACTION TYPE"))
        self.del_type = QComboBox()
        self.del_type.addItems(["Deactivate Account", "Delete Customer (Cascade)"])
        self.del_type.setStyleSheet(StyleSheet.COMBO_BOX)
        layout.addWidget(self.del_type)

        layout.addSpacing(10)
        layout.addWidget(QLabel("TARGET RECORD ID"))
        self.del_id = QLineEdit()
        self.del_id.setPlaceholderText("Enter Numeric ID...")
        self.del_id.setValidator(QIntValidator())
        self.del_id.setStyleSheet(StyleSheet.LINE_EDIT)
        layout.addWidget(self.del_id)

        layout.addSpacing(30)
        btn: QPushButton = QPushButton("EXECUTE CHANGES")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c; height: 50px; border-radius: 12px; 
                font-weight: bold; color: white; font-size: 11pt;
            }
            QPushButton:hover { background: #c0392b; }
        """)
        btn.clicked.connect(self.handle_maintenance)
        layout.addWidget(btn)
        layout.addStretch()
        return page

    def _build_base_page(
        self,
        title: str,
        fields: List[Tuple[str, str, Optional[QValidator]]],
        btn_text: str,
        callback: Callable[[Dict[str, QLineEdit]], None]
    ) -> QWidget:
        page: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(page)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(10)

        header: QLabel = QLabel(title)
        header.setStyleSheet(
            """
            font-size: 20pt; 
            font-weight: 800; 
            color: white; 
            margin-bottom: 10px;
            """
        )
        layout.addWidget(header)

        inputs: Dict[str, QLineEdit] = {}
        for label, key, validator in fields:
            lbl: QLabel = QLabel(label.upper())
            lbl.setStyleSheet(
                f"""
                color: {DarkPalette.ACCENT_BLUE.name()}; 
                font-size: 8pt; 
                font-weight: bold;
                """
            )
            layout.addWidget(lbl)
            
            edit: QLineEdit = QLineEdit()
            edit.setPlaceholderText(f"e.g. {label.split()[-1]}...")
            edit.setStyleSheet(StyleSheet.LINE_EDIT)
            if validator:
                edit.setValidator(validator)
            layout.addWidget(edit)
            inputs[key] = edit

        layout.addSpacing(30)
        btn: QPushButton = QPushButton(btn_text)
        btn.setFixedHeight(55)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {DarkPalette.ACCENT_BLUE.name()}; 
                font-weight: 800; border-radius: 15px; color: white; font-size: 11pt;
            }}
            QPushButton:hover {{ background: {DarkPalette.ACCENT_BLUE.name()}cc; }}
        """)
        btn.clicked.connect(lambda: callback(inputs))
        layout.addWidget(btn)
        
        layout.addStretch()
        return page

    def handle_create_customer(self, inputs: Dict[str, QLineEdit]) -> None:
        try:
            name: str = inputs['txt_name'].text().strip()
            email: str = inputs['txt_email'].text().strip()
            score: int = int(inputs['num_score'].text() or 0)
            
            if not name or "@" not in email:
                raise ValueError("Valid Name and Email are required")

            new_cust = self.services['customer'].create_customer(name, email, score)
            self._success(f"Customer {name} (ID: {new_cust.id}) registered!")
            self._clear_inputs(inputs)
        except Exception as e:
            self._error(str(e))

    def handle_create_account(self, inputs: Dict[str, QLineEdit]) -> None:
        try:
            c_id: int = int(inputs['num_cust_id'].text())
            b_id: int = int(inputs['num_branch_id'].text())
            num: str = inputs['txt_acc_num'].text().strip()
            
            self.services['account'].create_account(c_id, b_id, num, "CHECKING")
            self._success(f"Account {num} is now active.")
            self._clear_inputs(inputs)
        except Exception as e:
            self._error(str(e))

    def handle_post_transaction(self, inputs: Dict[str, QLineEdit]) -> None:
        try:
            a_id: int = int(inputs['num_acc_id_tx'].text())
            amt: float = float(inputs['num_amount'].text().replace(',', '.'))
            cat: str = inputs['txt_cat'].text().strip()
            
            self.services['transaction'].create_transaction(a_id, amt, cat, "Manual System Entry")
            self._success(f"Funds ${amt} processed for Account {a_id}.")
            self._clear_inputs(inputs)
        except Exception as e:
            self._error(str(e))

    def handle_maintenance(self) -> None:
        m_type: str = self.del_type.currentText()
        target_id_text: str = self.del_id.text().strip()
        
        if not target_id_text:
            self._error("Target ID must be specified")
            return
            
        target_id: int = int(target_id_text)
        reply = QMessageBox.critical(
            self, '⚠️ SENSITIVE OPERATION', 
            f"You are about to {m_type.upper()} (ID: {target_id}).\n\nThis cannot be undone. Proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if "Account" in m_type:
                    self.services['account'].update_account_status(target_id, False)
                    self._success(f"Account {target_id} has been disabled.")
                else:
                    self.services['customer'].delete_customer(target_id)
                    self._success(f"Record {target_id} wiped from database.")
                self.del_id.clear()
            except Exception as e:
                self._error(str(e))
    
    def _clear_inputs(self, inputs: Dict[str, QLineEdit]) -> None:
        for edit in inputs.values():
            edit.clear()

    def _success(self, msg: str) -> None:
        self.status_label.setText(f"✅ {msg}")
        self.status_label.setStyleSheet(
            """
            color: #2ecc71; 
            font-weight: bold;
            margin-left: 10px;
            """
        )
        QTimer.singleShot(5000, lambda: self.status_label.setText("Ready for data operations..."))
        QTimer.singleShot(5000, lambda: self.status_label.setStyleSheet(
            """
            color: #888; 
            margin-left: 10px;
            """
        ))

    def _error(self, msg: str) -> None:
        self.status_label.setText(f"❌ {msg[:60]}...")
        self.status_label.setStyleSheet(
            """
            color: #e74c3c; 
            font-weight: bold; 
            margin-left: 10px;
            """
        )