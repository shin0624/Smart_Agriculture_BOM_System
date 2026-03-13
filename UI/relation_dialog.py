
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QComboBox, QTableWidget,
                                QTableWidgetItem, QDialogButtonBox,
                                QHeaderView, QPushButton)
from PySide6.QtCore import Qt, QTimer
from DB.part_repo import search_parts, get_relation_notes_map

RELATION_TYPES = ["함께사용", "대체가능", "상위부품", "하위부품"]

class RelationDialog(QDialog):
    def __init__(self, exclude_id: int, parent=None):
        super().__init__(parent)
        self._exclude_id = exclude_id
        self._relation_notes = get_relation_notes_map(exclude_id)
        self.selected_part_id = None
        self.selected_relation_type = ""
        self.note = ""
        self.setWindowTitle("연관 부품 추가")
        self.resize(560, 480)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("연관 부품 검색"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("부품명 또는 부품번호 입력...")
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["부품번호", "부품명", "카테고리", "메모"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        h = QHBoxLayout()
        h.addWidget(QLabel("관계 유형"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(RELATION_TYPES)
        h.addWidget(self.type_combo)
        h.addWidget(QLabel("메모"))
        self.note_input = QLineEdit()
        h.addWidget(self.note_input)
        layout.addLayout(h)

        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self._accept)
        bbox.rejected.connect(self.reject)
        layout.addWidget(bbox)

        self._timer = QTimer(); self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._search)
        self._search()

    def _on_search(self):
        self._timer.start(300)

    def _search(self):
        keyword = self.search_input.text().strip()
        rows = search_parts(keyword)
        self.table.setRowCount(0)
        for row in rows:
            if row["id"] == self._exclude_id:
                continue
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(row["part_number"] or ""))
            self.table.setItem(r, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(row["category_name"] or ""))
            self.table.setItem(r, 3, QTableWidgetItem(self._relation_notes.get(row["id"], "")))
            self.table.item(r, 0).setData(Qt.UserRole, row["id"])

    def _accept(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = self.table.currentRow()
        self.selected_part_id = self.table.item(row, 0).data(Qt.UserRole)
        self.selected_relation_type = self.type_combo.currentText()
        self.note = self.note_input.text().strip()
        self.accept()
