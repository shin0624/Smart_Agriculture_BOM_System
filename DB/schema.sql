PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    parent_id   INTEGER REFERENCES categories(id),
    description TEXT
);

CREATE TABLE IF NOT EXISTS machinery_types (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT,
    image_path  TEXT
);

CREATE TABLE IF NOT EXISTS manufacturers (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    country TEXT,
    contact TEXT,
    website TEXT
);

CREATE TABLE IF NOT EXISTS parts (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number        TEXT UNIQUE,
    name               TEXT NOT NULL,
    category_id        INTEGER REFERENCES categories(id),
    manufacturer_id    INTEGER REFERENCES manufacturers(id),
    description        TEXT,
    image_path         TEXT,
    unit               TEXT DEFAULT '개',
    unit_price         REAL DEFAULT 0,
    stock_quantity     INTEGER DEFAULT 0,
    min_stock_alert    INTEGER DEFAULT 0,
    created_at         TEXT DEFAULT (datetime('now','localtime')),
    updated_at         TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS part_specifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id     INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    spec_key    TEXT NOT NULL,
    spec_value  TEXT NOT NULL,
    sort_order  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS part_machinery (
    part_id      INTEGER REFERENCES parts(id) ON DELETE CASCADE,
    machinery_id INTEGER REFERENCES machinery_types(id),
    model_note   TEXT,
    PRIMARY KEY (part_id, machinery_id)
);

CREATE TABLE IF NOT EXISTS part_relations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id_a     INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    part_id_b     INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    note          TEXT,
    CHECK (part_id_a != part_id_b)
);

-- 기본 카테고리 데이터
INSERT OR IGNORE INTO categories (id, name, parent_id) VALUES
(1,  '엔진부품',   NULL),
(2,  '냉각계통',   1),
(3,  '연료계통',   1),
(4,  '윤활계통',   1),
(5,  '주행부품',   NULL),
(6,  '바퀴/타이어', 5),
(7,  '브레이크',   5),
(8,  '변속기',     5),
(9,  '전기장치',   NULL),
(10, '배터리/발전', 9),
(11, '조명',       9),
(12, '외장/프레임', NULL),
(13, '유압계통',   NULL),
(14, '작업기부품',  NULL);

-- 기본 농기계 종류
INSERT OR IGNORE INTO machinery_types (id, name) VALUES
(1, '트랙터'),
(2, '경운기'),
(3, '콤바인'),
(4, '이앙기'),
(5, '바인더'),
(6, '관리기'),
(7, '굴착기'),
(8, '파종기'),
(9, '로더');
