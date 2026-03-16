
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
                                QComboBox, QPushButton, QTableWidget,
                                QTableWidgetItem, QLabel, QSplitter, QHeaderView,
                                QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from DB.part_repo import search_parts
from DB.lookup_repo import get_all_categories, get_all_machinery_types
from UI.part_detail_widget import PartDetailWidget
from UI.part_form_dialog import PartFormDialog

class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._load_filters()
        self._search()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Horizontal)

        # ── 좌측 패널 ──
        left = QWidget()
        left.setFixedWidth(320)
        lv = QVBoxLayout(left)
        lv.setSpacing(6)

        lv.addWidget(QLabel("부품 검색"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("부품명 / 부품번호 / 설명 검색...")
        self.search_input.textChanged.connect(self._on_search_changed)
        lv.addWidget(self.search_input)

        lv.addWidget(QLabel("카테고리"))
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self._search)
        lv.addWidget(self.category_combo)

        lv.addWidget(QLabel("농기계 종류"))
        self.machinery_combo = QComboBox()
        self.machinery_combo.currentIndexChanged.connect(self._search)
        lv.addWidget(self.machinery_combo)

        btn_new = QPushButton("＋ 신규 부품 등록")
        btn_new.setStyleSheet("background:#2196F3;color:white;padding:8px;font-weight:bold;border-radius:4px;")
        btn_new.clicked.connect(self._open_new_part)
        lv.addWidget(btn_new)

        lv.addWidget(QLabel("검색 결과"))
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["부품번호", "부품명", "카테고리", "재고"])
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.itemSelectionChanged.connect(self._on_select)
        lv.addWidget(self.result_table)

        self.count_label = QLabel("총 0 건")
        self.count_label.setStyleSheet("color:gray;font-size:11px;")
        lv.addWidget(self.count_label)

        # ── 우측 패널 ──
        self.detail_widget = PartDetailWidget()
        self.detail_widget.part_changed.connect(self._search)

        splitter.addWidget(left)
        splitter.addWidget(self.detail_widget)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._search)

    def _load_filters(self):
        self.category_combo.addItem("전체 카테고리", None)
        for row in get_all_categories():
            prefix = "  └ " if row["parent_id"] else ""
            self.category_combo.addItem(prefix + row["name"], row["id"])

        self.machinery_combo.addItem("전체 농기계", None)
        for row in get_all_machinery_types():
            self.machinery_combo.addItem(row["name"], row["id"])

    def _on_search_changed(self):
        self._timer.start(300)

    def _search(self):
        keyword = self.search_input.text().strip()
        cat_id = self.category_combo.currentData()
        mach_id = self.machinery_combo.currentData()
        rows = search_parts(keyword, cat_id, mach_id)

        self.result_table.setRowCount(0)
        for row in rows:
            r = self.result_table.rowCount()
            self.result_table.insertRow(r)
            self.result_table.setItem(r, 0, QTableWidgetItem(row["part_number"] or ""))
            self.result_table.setItem(r, 1, QTableWidgetItem(row["name"]))
            self.result_table.setItem(r, 2, QTableWidgetItem(row["category_name"] or ""))
            qty_item = QTableWidgetItem(str(row["stock_quantity"]))
            qty_item.setTextAlignment(Qt.AlignCenter)
            if row["stock_quantity"] == 0:
                qty_item.setForeground(QColor("#e53935"))
            self.result_table.setItem(r, 3, qty_item)
            self.result_table.item(r, 0).setData(Qt.UserRole, row["id"])

        self.count_label.setText(f"총 {len(rows)} 건")

    def _on_select(self):
        selected = self.result_table.selectedItems()
        if not selected:
            return
        row = self.result_table.currentRow()
        part_id = self.result_table.item(row, 0).data(Qt.UserRole)
        self.detail_widget.load_part(part_id)

    def _open_new_part(self):
        dlg = PartFormDialog(parent=self)
        if dlg.exec():
            self._search()
