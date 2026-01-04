import sys
from typing import Dict, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTabWidget, QLabel, QMessageBox, QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction

from app.core.services.account import AccountService
from app.core.services.branch import BranchService
from app.core.services.customer import CustomerService
from app.core.services.dailybalance import DailyBalanceService
from app.core.services.datedim import DateDimService
from app.core.services.transaction import TransactionService

from app.ui.components.tabs.account_explorer import AccountExplorerTab
from app.ui.components.tabs.advance_data_explorer import AdvancedDataExplorerTab
from app.ui.components.tabs.balance_analytics import BalanceAnalyticsTab
from app.ui.components.tabs.branch_analytics import BranchAnalyticsTab
from app.ui.components.tabs.customer_analytics import CustomerAnalyticsTab
from app.ui.components.tabs.data_management import DataManagementTab
from app.ui.components.tabs.transaction_analytics import TransactionAnalyticsTab

from app.ui.styles import StyleSheet, DarkPalette
from app.ui.components.sidebar import SidebarWidget
from app.ui.components.widgets.header import HeaderWidget

from app.db.base import get_db

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.services: Dict[str, Any]
        
        self.main_layout: QHBoxLayout
        self.content_layout: QVBoxLayout
        self.sidebar: SidebarWidget
        self.header: HeaderWidget
        self.tabs: QTabWidget
        
        self.tab_explorer: AccountExplorerTab
        self.tab_management: DataManagementTab
        
        self.kpi_widgets: Dict[str, QLabel] = {}
        
        self.setWindowTitle("MORDOR | Data Intelligence System")
        self.setMinimumSize(1450, 900)
        self.setStyleSheet(StyleSheet.MAIN_WINDOW)
        
        try:
            self.init_services()
            self.init_ui()
            self.connect_sidebar_signals()
            
            QTimer.singleShot(500, self.update_global_data)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Critical Startup Error", 
                f"System failure: {str(e)}"
            )
            sys.exit(1)

    def init_services(self) -> None:
        db = next(get_db())
        self.services = {
            'account': AccountService(db),
            'branch': BranchService(db),
            'customer': CustomerService(db),
            'daily_balance': DailyBalanceService(db),
            'date_dim': DateDimService(db),
            'transaction': TransactionService(db)
        }

    def init_ui(self) -> None:
        central_widget: QWidget = QWidget()
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.sidebar = SidebarWidget(self.services)
        self.main_layout.addWidget(self.sidebar)
        
        content_wrapper: QWidget = QWidget()
        self.content_layout = QVBoxLayout(content_wrapper)
        self.content_layout.setContentsMargins(25, 20, 25, 20)
        self.content_layout.setSpacing(20)
        
        self.header = HeaderWidget()
        self.content_layout.addWidget(self.header)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(StyleSheet.TAB_WIDGET)
        self._setup_tabs()
        self.content_layout.addWidget(self.tabs)
        
        self.main_layout.addWidget(content_wrapper, 1)
        self.setCentralWidget(central_widget)
        
        self.create_menu_bar()
        self._setup_status_bar()

    def _setup_tabs(self) -> None:
        self.tab_explorer = AccountExplorerTab(self.services)
        self.tab_management = DataManagementTab(self.services)
        
        self.tabs.addTab(
            TransactionAnalyticsTab(self.services), 
            "📊 Transaction Analytics"
        )
        self.tabs.addTab(
            CustomerAnalyticsTab(self.services), 
            "👥 Credit Intelligence"
        )
        self.tabs.addTab(
            BranchAnalyticsTab(self.services), 
            "🏢 Branch Performance"
        )
        self.tabs.addTab(
            BalanceAnalyticsTab(self.services), 
            "💰 Balance Analytics"
        )
        self.tabs.addTab(
            self.tab_explorer, 
            "🔍 Account Explorer"
        )
        self.tabs.addTab(
            AdvancedDataExplorerTab(self.services), 
            "🧠 Data Explorer"
        )
        self.tabs.addTab(
            self.tab_management, 
            "🛠 Data Management"
        )

    def connect_sidebar_signals(self) -> None:
        self.sidebar.refresh_requested.connect(self.update_global_data)
        
        self.sidebar.filters_changed.connect(self.apply_global_filters)
        
        self.sidebar.collapsed_toggled.connect(self.handle_sidebar_resize)

    def update_global_data(self) -> None:
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("Synchronizing database...", 2000)
        
        try:
            customers_count: int = self.services['customer'].count_all()
            if "CLIENT BASE" in self.kpi_widgets:
                self.kpi_widgets["CLIENT BASE"].setText(f"{customers_count:,}")
            
            current_tab: Optional[QWidget] = self.tabs.currentWidget()
            if current_tab and hasattr(current_tab, 'refresh_data'):
                current_tab.refresh_data()
            
            if status_bar:
                status_bar.showMessage("Data updated successfully", 3000)
        except Exception as e:
            if status_bar:
                status_bar.showMessage(f"Sync error: {str(e)}")

    def apply_global_filters(self, filters: Dict[str, str]) -> None:
        region: str = filters.get('region', '')
        segment: str = filters.get('segment', '')
        
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(f"Filter set: {region} | {segment}", 3000)
        
        current_tab: Optional[QWidget] = self.tabs.currentWidget()
        if current_tab and hasattr(current_tab, 'set_filters'):
            current_tab.set_filters(filters)

    def handle_sidebar_resize(self, is_collapsed: bool) -> None:
        margin: int = 15 if is_collapsed else 25
        self.content_layout.setContentsMargins(margin, 20, margin, 20)

    def _setup_status_bar(self) -> None:
        """Configure the status bar with styling and version info."""
        sb: QStatusBar = self.statusBar()
        sb.setStyleSheet(
            f"background: {DarkPalette.BG_MEDIUM.name()}; "
            f"color: #888; border-top: 1px solid #333;"
        )
        version_label: QLabel = QLabel(
            f"V1.2.4-STABLE | {datetime.now().year} "
        )
        sb.addPermanentWidget(version_label)

    def create_menu_bar(self) -> None:
        mb: QMenuBar = self.menuBar()
        mb.setStyleSheet(
            f"background: {DarkPalette.BG_MEDIUM.name()}; "
            f"color: white; border-bottom: 1px solid #333;"
        )
        
        file_menu: QMenu = mb.addMenu("File")
        file_menu.addAction("Export Data", lambda: print("Exporting..."))
        file_menu.addSeparator()
        
        exit_act: QAction = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        
        view_menu: QMenu = mb.addMenu("View")
        fs_act: QAction = QAction("Toggle Fullscreen", self)
        fs_act.setShortcut("F11")
        fs_act.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fs_act)

    def toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()