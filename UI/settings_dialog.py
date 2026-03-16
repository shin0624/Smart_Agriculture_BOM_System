
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                                QWidget, QListWidget, QPushButton, QInputDialog,
                                QComboBox, QLabel, QLineEdit, QFormLayout,
                                QDialogButtonBox, QMessageBox)
from DB.lookup_repo import (get_all_categories, get_all_manufacturers,
                             get_all_machinery_types, insert_category,
                             insert_manufacturer, insert_machinery_type)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("기준 정보 관리")
        self.resize(500, 500)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        tabs.addTab(self._build_category_tab(), "카테고리")
        tabs.addTab(self._build_manufacturer_tab(), "제조사")
        tabs.addTab(self._build_machinery_tab(), "농기계 종류")

        layout.addWidget(tabs)
        btn = QPushButton("닫기")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def _build_category_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.cat_list = QListWidget()
        self._refresh_categories()
        v.addWidget(self.cat_list)
        h = QHBoxLayout()
        btn_add = QPushButton("추가")
        btn_add.clicked.connect(self._add_category)
        h.addWidget(btn_add); h.addStretch()
        v.addLayout(h)
        return w

    def _refresh_categories(self):
        self.cat_list.clear()
        for c in get_all_categories():
            prefix = "  └ " if c["parent_id"] else ""
            self.cat_list.addItem(prefix + c["name"])

    def _add_category(self):
        name, ok = QInputDialog.getText(self, "카테고리 추가", "카테고리명:")
        if ok and name.strip():
            insert_category(name.strip())
            self._refresh_categories()

    def _build_manufacturer_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.mfr_list = QListWidget()
        self._refresh_manufacturers()
        v.addWidget(self.mfr_list)
        h = QHBoxLayout()
        btn_add = QPushButton("추가")
        btn_add.clicked.connect(self._add_manufacturer)
        h.addWidget(btn_add); h.addStretch()
        v.addLayout(h)
        return w

    def _refresh_manufacturers(self):
        self.mfr_list.clear()
        for m in get_all_manufacturers():
            self.mfr_list.addItem(m["name"])

    def _add_manufacturer(self):
        name, ok = QInputDialog.getText(self, "제조사 추가", "제조사명:")
        if ok and name.strip():
            insert_manufacturer(name.strip())
            self._refresh_manufacturers()

    def _build_machinery_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.mach_list = QListWidget()
        self._refresh_machinery()
        v.addWidget(self.mach_list)
        h = QHBoxLayout()
        btn_add = QPushButton("추가")
        btn_add.clicked.connect(self._add_machinery)
        h.addWidget(btn_add); h.addStretch()
        v.addLayout(h)
        return w

    def _refresh_machinery(self):
        self.mach_list.clear()
        for m in get_all_machinery_types():
            self.mach_list.addItem(m["name"])

    def _add_machinery(self):
        name, ok = QInputDialog.getText(self, "농기계 추가", "농기계명:")
        if ok and name.strip():
            insert_machinery_type(name.strip())
            self._refresh_machinery()
