
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QScrollArea, QFrame, QTableWidget,
                                QTableWidgetItem, QHeaderView, QMessageBox,
                                QGroupBox, QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
from DB.part_repo import get_part_detail, delete_part, delete_relation, add_relation
from UI.part_form_dialog import PartFormDialog
from UI.relation_dialog import RelationDialog

class PartDetailWidget(QWidget):
    part_changed = Signal()

    def __init__(self):
        super().__init__()
        self._current_id = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # 빈 상태 안내
        self.empty_label = QLabel("← 좌측에서 부품을 선택하세요")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color:gray;font-size:15px;")
        layout.addWidget(self.empty_label)

        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(12)
        scroll.setWidget(self.content)
        layout.addWidget(scroll)

        self.scroll = scroll
        self.scroll.setVisible(False)

        self._build_header()
        self._build_specs()
        self._build_machineries()
        self._build_relations()

    def _build_header(self):
        hbox = QHBoxLayout()

        # 이미지
        self.img_label = QLabel()
        self.img_label.setFixedSize(160, 160)
        self.img_label.setStyleSheet("border:1px solid #ddd;background:#f5f5f5;border-radius:6px;")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setText("이미지 없음")
        hbox.addWidget(self.img_label)

        # 기본 정보
        info_layout = QGridLayout()
        info_layout.setColumnStretch(1, 1)
        self.lbl_name = QLabel()
        font = QFont(); font.setPointSize(16); font.setBold(True)
        self.lbl_name.setFont(font)
        info_layout.addWidget(self.lbl_name, 0, 0, 1, 2)

        labels = ["부품번호", "카테고리", "제조사", "단가", "재고수량", "단위"]
        self.info_values = {}
        for i, lbl in enumerate(labels):
            info_layout.addWidget(QLabel(f"<b>{lbl}</b>"), i+1, 0)
            val = QLabel()
            val.setWordWrap(True)
            info_layout.addWidget(val, i+1, 1)
            self.info_values[lbl] = val

        hbox.addLayout(info_layout)
        self.content_layout.addLayout(hbox)

        # 설명
        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color:#555;padding:4px;")
        self.content_layout.addWidget(self.lbl_desc)

        # 버튼
        btn_layout = QHBoxLayout()
        btn_edit = QPushButton("수정")
        btn_edit.setStyleSheet("background:#FF9800;color:white;padding:6px 16px;border-radius:4px;")
        btn_edit.clicked.connect(self._edit_part)
        btn_del = QPushButton("삭제")
        btn_del.setStyleSheet("background:#f44336;color:white;padding:6px 16px;border-radius:4px;")
        btn_del.clicked.connect(self._delete_part)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_del)
        btn_layout.addStretch()
        self.content_layout.addLayout(btn_layout)

    def _build_specs(self):
        grp = QGroupBox("규격 정보")
        vbox = QVBoxLayout(grp)
        self.spec_table = QTableWidget(0, 2)
        self.spec_table.setHorizontalHeaderLabels(["항목", "값"])
        self.spec_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.spec_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.spec_table.verticalHeader().setVisible(False)
        self.spec_table.setMaximumHeight(150)
        vbox.addWidget(self.spec_table)
        self.content_layout.addWidget(grp)

    def _build_machineries(self):
        grp = QGroupBox("적용 농기계")
        vbox = QVBoxLayout(grp)
        self.machinery_label = QLabel()
        self.machinery_label.setWordWrap(True)
        vbox.addWidget(self.machinery_label)
        self.content_layout.addWidget(grp)

    def _build_relations(self):
        grp = QGroupBox("연관 부품")
        vbox = QVBoxLayout(grp)

        btn_add_rel = QPushButton("＋ 연관 부품 추가")
        btn_add_rel.setStyleSheet("background:#4CAF50;color:white;padding:4px 12px;border-radius:4px;")
        btn_add_rel.clicked.connect(self._add_relation)
        vbox.addWidget(btn_add_rel)

        self.relation_table = QTableWidget(0, 5)
        self.relation_table.setHorizontalHeaderLabels(["관계", "부품번호", "부품명", "메모", "삭제"])
        self.relation_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.relation_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.relation_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.relation_table.verticalHeader().setVisible(False)
        self.relation_table.setMaximumHeight(180)
        vbox.addWidget(self.relation_table)
        self.content_layout.addWidget(grp)

    def load_part(self, part_id: int):
        self._current_id = part_id
        part, specs, machineries, relations = get_part_detail(part_id)

        self.empty_label.setVisible(False)
        self.scroll.setVisible(True)

        self.lbl_name.setText(part["name"])
        self.lbl_desc.setText(part["description"] or "")
        self.info_values["부품번호"].setText(part["part_number"] or "-")
        self.info_values["카테고리"].setText(part["category_name"] or "-")
        self.info_values["제조사"].setText(part["manufacturer_name"] or "-")
        self.info_values["단가"].setText(f"{int(part['unit_price']):,} 원" if part["unit_price"] else "-")
        qty = part["stock_quantity"]
        qty_text = f"{qty} {part['unit']}"
        self.info_values["재고수량"].setText(qty_text)
        self.info_values["재고수량"].setStyleSheet("color:#e53935;font-weight:bold;" if qty == 0 else "")
        self.info_values["단위"].setText(part["unit"] or "개")

        # 이미지
        img_path = part["image_path"]
        if img_path:
            import os
            if os.path.exists(img_path):
                pix = QPixmap(img_path).scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.img_label.setPixmap(pix)
            else:
                self.img_label.setText("이미지 없음")
                self.img_label.setPixmap(QPixmap())
        else:
            self.img_label.setText("이미지 없음")
            self.img_label.setPixmap(QPixmap())

        # 규격
        self.spec_table.setRowCount(0)
        for s in specs:
            r = self.spec_table.rowCount()
            self.spec_table.insertRow(r)
            self.spec_table.setItem(r, 0, QTableWidgetItem(s["spec_key"]))
            self.spec_table.setItem(r, 1, QTableWidgetItem(s["spec_value"]))

        # 농기계
        names = [f"{m['name']}" + (f" ({m['model_note']})" if m["model_note"] else "") for m in machineries]
        self.machinery_label.setText("  /  ".join(names) if names else "지정된 농기계 없음")

        # 연관 부품
        self.relation_table.setRowCount(0)
        self._relation_ids = {}
        for rel in relations:
            r = self.relation_table.rowCount()
            self.relation_table.insertRow(r)
            self.relation_table.setItem(r, 0, QTableWidgetItem(rel["relation_type"]))
            self.relation_table.setItem(r, 1, QTableWidgetItem(rel["related_number"] or ""))
            self.relation_table.setItem(r, 2, QTableWidgetItem(rel["related_name"]))
            self.relation_table.setItem(r, 3, QTableWidgetItem(rel["note"] or ""))
            btn_del = QPushButton("삭제")
            btn_del.setStyleSheet("color:red;")
            rel_id = rel["id"]
            btn_del.clicked.connect(lambda _, rid=rel_id: self._remove_relation(rid))
            self.relation_table.setCellWidget(r, 4, btn_del)

    def _edit_part(self):
        if not self._current_id:
            return
        dlg = PartFormDialog(part_id=self._current_id, parent=self)
        if dlg.exec():
            self.load_part(self._current_id)
            self.part_changed.emit()

    def _delete_part(self):
        if not self._current_id:
            return
        reply = QMessageBox.question(self, "삭제 확인", "이 부품을 삭제하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_part(self._current_id)
            self._current_id = None
            self.empty_label.setVisible(True)
            self.scroll.setVisible(False)
            self.part_changed.emit()

    def _add_relation(self):
        if not self._current_id:
            return
        dlg = RelationDialog(exclude_id=self._current_id, parent=self)
        if dlg.exec():
            add_relation(self._current_id, dlg.selected_part_id,
                         dlg.selected_relation_type, dlg.note)
            self.load_part(self._current_id)

    def _remove_relation(self, relation_id):
        delete_relation(relation_id)
        self.load_part(self._current_id)
