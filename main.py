import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from DB.database import Database
from UI.main_window import MainWindow

def main():
    # DB 초기화
    Database.get_connection()

    app = QApplication(sys.argv)
    app.setFont(QFont("맑은 고딕", 10))
    app.setStyle("Fusion")

    # 밝은 흰색 테마
    app.setStyleSheet("""
        QWidget {
            background-color: #ffffff;
            color: #111111;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
        }
        QTableWidget {
            gridline-color: #e6e6e6;
        }
        QHeaderView::section {
            background-color: #f5f5f5;
            padding: 4px;
            border: none;
            border-bottom: 1px solid #e0e0e0;
            font-weight: bold;
        }
        QPushButton {
            border-radius: 4px;
            padding: 5px 12px;
        }
        QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox {
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            padding: 4px;
            background-color: #ffffff;
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #90caf9;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
