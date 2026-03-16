import sqlite3
import os
import sys

def get_base_path():
    """PyInstaller 실행 시 임시 경로, 개발 시 현재 경로 반환"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__ + "/.."))

BASE_PATH = get_base_path()
DB_PATH = os.path.join(BASE_PATH, "app.db")
SCHEMA_PATH = os.path.join(BASE_PATH, "DB", "schema.sql")
ASSETS_PARTS_PATH = os.path.join(BASE_PATH, "Assets", "Parts")

class Database:
    _instance = None

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        if cls._instance is None:
            os.makedirs(ASSETS_PARTS_PATH, exist_ok=True)
            cls._instance = sqlite3.connect(DB_PATH, check_same_thread=False)
            cls._instance.row_factory = sqlite3.Row
            cls._instance.execute("PRAGMA foreign_keys = ON")
            cls._init_schema()
        return cls._instance

    @classmethod
    def _init_schema(cls):
        if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                cls._instance.executescript(f.read())
            cls._instance.commit()
        else:
            # 테이블 없으면 생성
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                cls._instance.executescript(f.read())
            cls._instance.commit()
