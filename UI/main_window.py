
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                                QVBoxLayout, QTabWidget, QStatusBar, QLabel)
from PySide6.QtCore import Qt
from UI.search_widget import SearchWidget
from UI.settings_dialog import SettingsDialog
from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("스마트 농업기계 BOM 시스템")
        self.resize(1280, 800)
        self._build_menu()
        self._build_ui()
        self._build_statusbar()

    def _build_menu(self):
        menu = self.menuBar()
        settings_menu = menu.addMenu("기준 정보 관리")
        act = QAction("카테고리 / 제조사 / 농기계 관리", self)
        act.triggered.connect(self._open_settings)
        settings_menu.addAction(act)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search_widget = SearchWidget()
        layout.addWidget(self.search_widget)

    def _build_statusbar(self):
        self.status_label = QLabel("준비")
        self.statusBar().addWidget(self.status_label)

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
