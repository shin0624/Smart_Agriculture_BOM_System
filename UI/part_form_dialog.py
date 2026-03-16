
import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                                QLineEdit, QComboBox, QTextEdit, QPushButton,
                                QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
                                QHeaderView, QDialogButtonBox, QGroupBox,
                                QCheckBox, QScrollArea, QWidget, QFrame, QSpinBox,
                                QDoubleSpinBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from DB.part_repo import (get_part_detail, insert_part, update_part,
                           save_specs, save_machineries)
from DB.lookup_repo import (get_all_categories, get_all_manufacturers,
                             get_all_machinery_types, insert_manufacturer,
                             update_manufacturer, delete_manufacturer)
from Utils.image_helper import save_part_image, delete_part_image
import os

class PartFormDialog(QDialog):
    def __init__(self, part_id=None, parent=None):
        super().__init__(parent)
        self._part_id = part_id
        self._image_src = None
        self._image_cleared = False
        self._image_path_current = None
        self.setWindowTitle("부품 등록" if not part_id else "부품 수정")
        self.resize(700, 750)
        self._build_ui()
        if part_id:
            self._load_data()

    def _build_ui(self):
        root = QVBoxLayout(self)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        scroll.setWidget(content)
        root.addWidget(scroll)

        # ── 기본 정보 ──
        grp1 = QGroupBox("기본 정보")
        form = QFormLayout(grp1)

        self.f_part_number = QLineEdit(); self.f_part_number.setPlaceholderText("예) TRC-W-001")
        self.f_name = QLineEdit(); self.f_name.setPlaceholderText("부품명 (필수)")
        self.f_category = QComboBox()
        self.f_category.addItem("선택 안함", None)
        for c in get_all_categories():
            prefix = "  └ " if c["parent_id"] else ""
            self.f_category.addItem(prefix + c["name"], c["id"])

        self.f_manufacturer = QComboBox()
        self._load_manufacturers()
        btn_add_manufacturer = QPushButton("＋")
        btn_add_manufacturer.setFixedWidth(28)
        btn_add_manufacturer.clicked.connect(self._add_manufacturer_inline)
        btn_edit_manufacturer = QPushButton("수정")
        btn_edit_manufacturer.clicked.connect(self._edit_manufacturer_inline)
        btn_del_manufacturer = QPushButton("삭제")
        btn_del_manufacturer.clicked.connect(self._delete_manufacturer_inline)
        mfr_row = QHBoxLayout()
        mfr_row.addWidget(self.f_manufacturer)
        mfr_row.addWidget(btn_add_manufacturer)
        mfr_row.addWidget(btn_edit_manufacturer)
        mfr_row.addWidget(btn_del_manufacturer)

        self.f_description = QTextEdit(); self.f_description.setFixedHeight(60)
        self.f_unit = QLineEdit("개")
        self.f_unit_price = QDoubleSpinBox(); self.f_unit_price.setRange(0, 99999999); self.f_unit_price.setSuffix(" 원"); self.f_unit_price.setGroupSeparatorShown(True)
        self.f_stock = QSpinBox(); self.f_stock.setRange(0, 999999)
        self.f_min_alert = QSpinBox(); self.f_min_alert.setRange(0, 999999)

        form.addRow("부품번호", self.f_part_number)
        form.addRow("부품명 *", self.f_name)
        form.addRow("카테고리", self.f_category)
        form.addRow("제조사", mfr_row)
        form.addRow("설명", self.f_description)
        form.addRow("단위", self.f_unit)
        form.addRow("단가", self.f_unit_price)
        form.addRow("재고수량", self.f_stock)
        form.addRow("최소재고 경고", self.f_min_alert)
        layout.addWidget(grp1)

        # ── 이미지 ──
        grp_img = QGroupBox("부품 이미지")
        img_layout = QHBoxLayout(grp_img)
        self.img_preview = QLabel("이미지 없음")
        self.img_preview.setFixedSize(120, 120)
        self.img_preview.setAlignment(Qt.AlignCenter)
        self.img_preview.setStyleSheet("border:1px solid #ccc;background:#f9f9f9;border-radius:4px;")
        btn_img = QPushButton("이미지 선택")
        btn_img.clicked.connect(self._pick_image)
        btn_clear = QPushButton("이미지 제거")
        btn_clear.clicked.connect(self._clear_image)
        img_layout.addWidget(self.img_preview)
        vimg = QVBoxLayout()
        vimg.addWidget(btn_img); vimg.addWidget(btn_clear); vimg.addStretch()
        img_layout.addLayout(vimg)
        layout.addWidget(grp_img)

        # ── 규격 ──
        grp_spec = QGroupBox("규격 정보")
        spec_v = QVBoxLayout(grp_spec)
        self.spec_table = QTableWidget(0, 2)
        self.spec_table.setHorizontalHeaderLabels(["항목명", "값"])
        self.spec_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.spec_table.setFixedHeight(160)
        self.spec_table.verticalHeader().setVisible(False)
        spec_v.addWidget(self.spec_table)
        btn_add_spec = QPushButton("+ 규격 행 추가")
        btn_add_spec.clicked.connect(self._add_spec_row)
        btn_del_spec = QPushButton("선택 행 삭제")
        btn_del_spec.clicked.connect(self._del_spec_row)
        sh = QHBoxLayout(); sh.addWidget(btn_add_spec); sh.addWidget(btn_del_spec); sh.addStretch()
        spec_v.addLayout(sh)
        layout.addWidget(grp_spec)

        # ── 농기계 ──
        grp_mach = QGroupBox("적용 농기계")
        mach_v = QVBoxLayout(grp_mach)
        self.mach_checks = {}
        self.mach_notes = {}
        for mt in get_all_machinery_types():
            row_w = QWidget(); rh = QHBoxLayout(row_w); rh.setContentsMargins(0,0,0,0)
            cb = QCheckBox(mt["name"]); cb.setFixedWidth(100)
            note = QLineEdit(); note.setPlaceholderText("모델 메모 (선택)")
            self.mach_checks[mt["id"]] = cb
            self.mach_notes[mt["id"]] = note
            rh.addWidget(cb); rh.addWidget(note)
            mach_v.addWidget(row_w)
        layout.addWidget(grp_mach)

        # 버튼
        bbox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self._save)
        bbox.rejected.connect(self.reject)
        root.addWidget(bbox)

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "",
                                               "이미지 파일 (*.jpg *.jpeg *.png *.bmp)")
        if path:
            self._image_src = path
            self._image_cleared = False
            pix = QPixmap(path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_preview.setPixmap(pix)

    def _clear_image(self):
        self._image_src = None
        self._image_cleared = True
        self.img_preview.setPixmap(QPixmap())
        self.img_preview.setText("이미지 없음")

    def _add_spec_row(self):
        r = self.spec_table.rowCount()
        self.spec_table.insertRow(r)
        self.spec_table.setItem(r, 0, QTableWidgetItem(""))
        self.spec_table.setItem(r, 1, QTableWidgetItem(""))

    def _del_spec_row(self):
        row = self.spec_table.currentRow()
        if row >= 0:
            self.spec_table.removeRow(row)

    def _load_data(self):
        part, specs, machineries, _ = get_part_detail(self._part_id)
        self._image_path_current = part["image_path"]
        self.f_part_number.setText(part["part_number"] or "")
        self.f_name.setText(part["name"])
        self.f_description.setPlainText(part["description"] or "")
        self.f_unit.setText(part["unit"] or "개")
        self.f_unit_price.setValue(part["unit_price"] or 0)
        self.f_stock.setValue(part["stock_quantity"] or 0)
        self.f_min_alert.setValue(part["min_stock_alert"] or 0)

        for i in range(self.f_category.count()):
            if self.f_category.itemData(i) == part["category_id"]:
                self.f_category.setCurrentIndex(i); break
        self._select_manufacturer(part["manufacturer_id"])

        if part["image_path"] and os.path.exists(part["image_path"]):
            pix = QPixmap(part["image_path"]).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_preview.setPixmap(pix)
        else:
            self.img_preview.setPixmap(QPixmap())
            self.img_preview.setText("이미지 없음")

        for s in specs:
            r = self.spec_table.rowCount()
            self.spec_table.insertRow(r)
            self.spec_table.setItem(r, 0, QTableWidgetItem(s["spec_key"]))
            self.spec_table.setItem(r, 1, QTableWidgetItem(s["spec_value"]))

        machinery_ids = {m["machinery_id"] if "machinery_id" in m.keys() else 0 for m in machineries}
        # machinery_id 가져오기 우회
        from DB.database import Database
        rows = Database.get_connection().execute(
            "SELECT machinery_id, model_note FROM part_machinery WHERE part_id=?", (self._part_id,)
        ).fetchall()
        for row in rows:
            mid = row["machinery_id"]
            if mid in self.mach_checks:
                self.mach_checks[mid].setChecked(True)
                self.mach_notes[mid].setText(row["model_note"] or "")

    def _save(self):
        name = self.f_name.text().strip()
        if not name:
            QMessageBox.warning(self, "입력 오류", "부품명은 필수 항목입니다.")
            return

        data = {
            "part_number": self.f_part_number.text().strip() or None,
            "name": name,
            "category_id": self.f_category.currentData(),
            "manufacturer_id": self.f_manufacturer.currentData(),
            "description": self.f_description.toPlainText().strip(),
            "image_path": None,
            "unit": self.f_unit.text().strip() or "개",
            "unit_price": self.f_unit_price.value(),
            "stock_quantity": self.f_stock.value(),
            "min_stock_alert": self.f_min_alert.value(),
        }

        if self._part_id and not self._image_src and not self._image_cleared:
            data["image_path"] = self._image_path_current

        try:
            if self._part_id:
                update_part(self._part_id, data)
                pid = self._part_id
            else:
                pid = insert_part(data)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "입력 오류", "이미 사용 중인 부품번호입니다.")
            return

        if self._image_src:
            img_dest = save_part_image(self._image_src, pid)
            from DB.database import Database
            Database.get_connection().execute(
                "UPDATE parts SET image_path=? WHERE id=?", (img_dest, pid)
            )
            Database.get_connection().commit()
        elif self._part_id and self._image_cleared:
            delete_part_image(self._image_path_current)

        specs = []
        for r in range(self.spec_table.rowCount()):
            k = self.spec_table.item(r, 0)
            v = self.spec_table.item(r, 1)
            if k and v and k.text().strip():
                specs.append({"spec_key": k.text().strip(), "spec_value": v.text().strip()})
        save_specs(pid, specs)

        machinery_list = []
        for mid, cb in self.mach_checks.items():
            if cb.isChecked():
                machinery_list.append({"machinery_id": mid, "model_note": self.mach_notes[mid].text().strip()})
        save_machineries(pid, machinery_list)

        self.accept()

    def _load_manufacturers(self, selected_id=None):
        self.f_manufacturer.clear()
        self.f_manufacturer.addItem("선택 안함", None)
        for m in get_all_manufacturers():
            self.f_manufacturer.addItem(m["name"], m["id"])
        if selected_id is not None:
            self._select_manufacturer(selected_id)

    def _select_manufacturer(self, manufacturer_id):
        for i in range(self.f_manufacturer.count()):
            if self.f_manufacturer.itemData(i) == manufacturer_id:
                self.f_manufacturer.setCurrentIndex(i)
                break

    def _add_manufacturer_inline(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "제조사 추가", "제조사명:")
        if ok and name.strip():
            new_id = insert_manufacturer(name.strip())
            self._load_manufacturers(new_id)

    def _edit_manufacturer_inline(self):
        from PySide6.QtWidgets import QInputDialog
        manufacturer_id = self.f_manufacturer.currentData()
        if not manufacturer_id:
            QMessageBox.information(self, "알림", "수정할 제조사를 선택하세요.")
            return
        current_name = self.f_manufacturer.currentText()
        name, ok = QInputDialog.getText(self, "제조사 수정", "제조사명:", text=current_name)
        if ok and name.strip():
            update_manufacturer(manufacturer_id, name.strip())
            self._load_manufacturers(manufacturer_id)

    def _delete_manufacturer_inline(self):
        manufacturer_id = self.f_manufacturer.currentData()
        if not manufacturer_id:
            QMessageBox.information(self, "알림", "삭제할 제조사를 선택하세요.")
            return
        reply = QMessageBox.question(
            self,
            "삭제 확인",
            "선택한 제조사를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            delete_manufacturer(manufacturer_id)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "삭제 실패", "연결된 부품이 있어 삭제할 수 없습니다.")
            return
        self._load_manufacturers()
