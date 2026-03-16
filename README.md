# 스마트 농업기계 BOM 시스템

![MainWindow](/Images/Capture01.png)

## 개요

**1. 목적:** 농기계 부품의 조회·등록·재고관리를 오프라인 로컬 환경에서 운용하는 Windows 전용 데스크탑 프로그램  
**2. 대상 사용자:** 농기계 부품 판매/재고 관리 업체 담당자  
**3. 기술 스택**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt6-41CD52?logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image%20Processing-8A2BE2)
![PyInstaller](https://img.shields.io/badge/PyInstaller-Windows%20EXE%20Build-4B8BBE)
| 구분 | 채택 기술 | 이유 |
| :--- | :--- | :--- |
| 언어 | Python 3.11 | 빠른 개발, SQLite 내장 |
| UI 프레임워크 | PySide6 (Qt6) | 모던 UI, SQLite 드라이버 내장 |
| DB | SQLite3 | 인터넷 불필요, 단일 파일 관리 |
| 이미지 처리 | Pillow | 썸네일 생성, 이미지 리사이즈 |
| 빌드 | PyInstaller | .exe 단일 배포 |

---

## 기능 소개
### 부품 등록 : 부품 번호/부품 명/카테고리/제조사/단위/단가/재고수량/최소재고 경고/제품 이미지/규격 정보/적용 농기계 선택 가능
![BOM02](/Images/Capture02.png)
![BOM02_01](/Images/Capture03.png)

### 부품 조회 : 등록했던 부품 정보 조회/수정/삭제/연관 부품 추가 가능
![BOM3](/Images/Capture04.png)
![BOM4](/Images/Capture06.png)

### 연관 부품 추가
![BOM5](/Images/Capture05.png)

### 기준정보/제조사/농기계 종류 정보 추가
![BOM6](/Images/Capture07.png)
![BOM7](/Images/Capture08.png)
![BOM8](/Images/Capture09.png)

---

## 프로그램 아키텍처

### 1. 폴더 구조

```text
Smart_Agriculture_BOM_System/
├── main.py                # 엔트리포인트, App 초기화
├── app.db                 # SQLite DB 파일
├── Assets/
│   ├── Icons/             # UI 아이콘
│   └── Parts/             # 부품 이미지 저장 폴더
│       └── {part_id}.jpg
├── UI/
│   ├── main_window.py     # 메인 윈도우 (탭 구조)
│   ├── search_widget.py   # 부품 검색 화면
│   ├── part_detail_widget.py # 부품 상세 조회 화면
│   ├── part_form_dialog.py # 부품 등록/수정 다이얼로그
│   ├── relation_dialog.py # 연관 부품 추가 다이얼로그
│   └── settings_dialog.py # 카테고리/농기계/제조사 관리
├── DB/
│   ├── database.py        # DB 연결 싱글턴 관리
│   ├── schema.sql         # 테이블 정의 (초기화용)
│   ├── part_repo.py       # 부품 CRUD 레포지토리
│   └── lookup_repo.py     # 카테고리/제조사/농기계 조회
└── Utils/
    └── image_helper.py    # 이미지 저장/리사이즈
```

---

### 2. 레이어 구조 (3-Layer)

```text
┌──────────────────────────────────────────────────────────────────────────┐
│         UI Layer (PySide6)          │ ← 사용자 화면, 이벤트 처리          │
├──────────────────────────────────────────────────────────────────────────┤
│       Repository Layer (Python)     │ ← 비즈니스 로직, 검색/연관 로직     │
├──────────────────────────────────────────────────────────────────────────┤
│         Data Layer (SQLite3)        │ ← DB CRUD, 트랜잭션 관리            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## DB 구조

### 1. ERD 전체 개요

```text
categories ——< parts >—— manufacturers
             |
             ├──< part_specifications
             ├──< part_machinery >—— machinery_types
             └──< part_relations (자기참조 N:M)
```

### 2. 테이블 상세 정의

#### categories - 부품 카테고리 (계층형)

```sql
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,      -- 예: 엔진부품, 주행부품
    parent_id   INTEGER REFERENCES categories(id), -- NULL 이면 최상위
    description TEXT
);
-- 예시 계층:
-- 엔진부품 > 냉각계통
-- 주행부품 > 바퀴/타이어
-- 전기장치 > 배터리/발전
```

#### machinery_types - 농기계 종류

```sql
CREATE TABLE machinery_types (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE, -- 트랙터, 경운기, 콤바인 등
    description TEXT,
    image_path  TEXT
);
```

#### manufacturers - 제조사

```sql
CREATE TABLE manufacturers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL, -- 대동, LS 엠트론, 얀마 등
    country     TEXT,
    contact     TEXT,
    website     TEXT
);
```

#### parts - 부품 핵심 테이블

```sql
CREATE TABLE parts (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number      TEXT UNIQUE,          -- 부품 고유 번호 (바코드 등)
    name             TEXT NOT NULL,        -- 부품명
    category_id      INTEGER REFERENCES categories(id),
    manufacturer_id  INTEGER REFERENCES manufacturers(id),
    description      TEXT,                 -- 부품 설명
    image_path       TEXT,                 -- Assets/Parts/{id}.jpg
    unit             TEXT DEFAULT '개',    -- 수량 단위
    unit_price       REAL DEFAULT 0,       -- 단가
    stock_quantity   INTEGER DEFAULT 0,    -- 현재 재고
    min_stock_alert  INTEGER DEFAULT 0,    -- 최소 재고 경고선
    created_at       TEXT DEFAULT (datetime('now','localtime')),
    updated_at       TEXT DEFAULT (datetime('now','localtime'))
);
```

#### part_specifications - 부품 규격 (Key-Value)

```sql
CREATE TABLE part_specifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id     INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    spec_key    TEXT NOT NULL,  -- 무게, 크기, 재질, 규격번호, 마력 등
    spec_value  TEXT NOT NULL,  -- 2.3kg, 150x80mm, 철제 등
    sort_order  INTEGER DEFAULT 0
);
-- Key-Value 구조로 부품별 다른 규격 항목을 유연하게 저장
```

#### part_machinery - 부품 ↔ 농기계 연결 (N:M)

```sql
CREATE TABLE part_machinery (
    part_id      INTEGER REFERENCES parts(id) ON DELETE CASCADE,
    machinery_id INTEGER REFERENCES machinery_types(id),
    model_note   TEXT,  -- 특정 모델명 기재 (예: LS 트랙터 MT7 시리즈)
    PRIMARY KEY (part_id, machinery_id)
);
```

#### part_relations - 부품 간 연관관계 (핵심 기능)

```sql
CREATE TABLE part_relations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id_a     INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    part_id_b     INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    -- '함께사용': 같이 교체 권장
    -- '대체가능': 호환 대체 부품
    -- '상위부품': A 가 B 를 포함 (어셈블리)
    -- '하위부품': A 가 B 에 속함
    note          TEXT,
    CHECK (part_id_a != part_id_b)
);
```


---

## 유저 플로우

### 1. 전체 플로우

```text
[프로그램 실행]
      |
      ▼
[메인 화면] ————— 부품 검색 (기본 화면)
    |   ————— 기준 정보 관리 (카테고리/농기계/제조사)
      |
```
![MainWindow02](/Images/Capture01.png)


### 2. 핵심 기능: 부품 검색 플로우

```text
[검색창 입력]
부품명 OR 부품번호 OR 카테고리 선택
      |
      ▼
[실시간 검색 결과 리스트]
```


### 3. 부품 등록 플로우

```text
[부품 등록 버튼]
      |
      ▼
[부품 등록 다이얼로그]
      |
      ▼
[저장] → DB INSERT
```
![Part registration](/Images/Capture02.png)
![Part registration2](/Images/Capture03.png)

---

## 화면 구성 (UI 레이아웃)

### 1. 메인 윈도우
![MainWindow03](/Images/Capture04.png)


---

## 기능 목록 (우선순위별)

### Phase 1 - 핵심 기능 (필수)

- 부품 검색 (부품명, 부품번호, 카테고리, 농기계 유형 필터)
- 부품 상세 조회 (이미지, 규격, 연관 부품, 재고)
- 부품 등록 / 수정 / 삭제
- 연관 부품 등록 및 조회

### Phase 2 - 부가 기능

- 판매 기록 등록 및 조회
- 최소 재고 미달 경고 배지 표시
- 카테고리 / 제조사 / 농기계 종류 관리
- CSV 내보내기 (재고 현황, 판매 기록)

### Phase 3 - 확장 기능

- 바코드/QR 스캐너 연동 (부품번호 자동 입력)
- 인쇄 기능 (부품 카드, 재고 현황표)
- DB 백업 / 복원 기능 (app.db 파일 복사)

---

## 빌드 및 배포

PyInstaller 로 단일 폴더 빌드  
`app.db` 와 `assets/` 폴더는 실행파일과 **같은 경로**에 위치하도록 경로 처리하며,  
최초 실행 시 DB 가 없으면 `schema.sql` 을 기반으로 자동 생성

```bash
# 빌드 커맨드 예시
pyinstaller --noconfirm --onedir --windowed \
  --add-data "assets;assets" \
  --add-data "db/schema.sql;db" \
  --icon "assets/icons/app.ico" \
  main.py
```
