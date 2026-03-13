from DB.database import Database

def search_parts(keyword="", category_id=None, machinery_id=None):
    conn = Database.get_connection()
    query = """
        SELECT DISTINCT p.id, p.part_number, p.name, p.stock_quantity, p.unit_price, p.unit,
               c.name AS category_name, m.name AS manufacturer_name
        FROM parts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN manufacturers m ON p.manufacturer_id = m.id
        LEFT JOIN part_machinery pm ON p.id = pm.part_id
        WHERE 1=1
    """
    params = []
    if keyword:
        query += " AND (p.name LIKE ? OR p.part_number LIKE ? OR p.description LIKE ?)"
        params += [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
    if category_id:
        query += " AND (p.category_id = ? OR p.category_id IN (SELECT id FROM categories WHERE parent_id = ?))"
        params += [category_id, category_id]
    if machinery_id:
        query += " AND pm.machinery_id = ?"
        params.append(machinery_id)
    query += " ORDER BY p.name"
    return conn.execute(query, params).fetchall()


def get_part_detail(part_id):
    conn = Database.get_connection()
    part = conn.execute("""
        SELECT p.*, c.name AS category_name, m.name AS manufacturer_name
        FROM parts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN manufacturers m ON p.manufacturer_id = m.id
        WHERE p.id = ?
    """, (part_id,)).fetchone()

    specs = conn.execute(
        "SELECT spec_key, spec_value FROM part_specifications WHERE part_id = ? ORDER BY sort_order",
        (part_id,)
    ).fetchall()

    machineries = conn.execute("""
        SELECT mt.name, pm.model_note
        FROM part_machinery pm
        JOIN machinery_types mt ON pm.machinery_id = mt.id
        WHERE pm.part_id = ?
    """, (part_id,)).fetchall()

    relations = conn.execute("""
        SELECT pr.id, pr.relation_type, pr.note,
               p.id AS related_id, p.name AS related_name, p.part_number AS related_number
        FROM part_relations pr
        JOIN parts p ON (
            CASE WHEN pr.part_id_a = ? THEN pr.part_id_b ELSE pr.part_id_a END = p.id
        )
        WHERE pr.part_id_a = ? OR pr.part_id_b = ?
    """, (part_id, part_id, part_id)).fetchall()

    return part, specs, machineries, relations


def get_relation_notes_map(part_id: int) -> dict:
    conn = Database.get_connection()
    rows = conn.execute("""
        SELECT part_id_a, part_id_b, note
        FROM part_relations
        WHERE part_id_a = ? OR part_id_b = ?
    """, (part_id, part_id)).fetchall()

    notes = {}
    for row in rows:
        related_id = row["part_id_b"] if row["part_id_a"] == part_id else row["part_id_a"]
        notes[related_id] = row["note"] or ""
    return notes


def insert_part(data: dict) -> int:
    conn = Database.get_connection()
    cur = conn.execute("""
        INSERT INTO parts (part_number, name, category_id, manufacturer_id,
                           description, image_path, unit, unit_price,
                           stock_quantity, min_stock_alert)
        VALUES (:part_number, :name, :category_id, :manufacturer_id,
                :description, :image_path, :unit, :unit_price,
                :stock_quantity, :min_stock_alert)
    """, data)
    conn.commit()
    return cur.lastrowid


def update_part(part_id: int, data: dict):
    conn = Database.get_connection()
    data["id"] = part_id
    conn.execute("""
        UPDATE parts SET
            part_number=:part_number, name=:name, category_id=:category_id,
            manufacturer_id=:manufacturer_id, description=:description,
            image_path=:image_path, unit=:unit, unit_price=:unit_price,
            stock_quantity=:stock_quantity, min_stock_alert=:min_stock_alert,
            updated_at=datetime('now','localtime')
        WHERE id=:id
    """, data)
    conn.commit()


def delete_part(part_id: int):
    conn = Database.get_connection()
    conn.execute("DELETE FROM parts WHERE id=?", (part_id,))
    conn.commit()


def save_specs(part_id: int, specs: list):
    """specs: [{"spec_key": str, "spec_value": str}, ...]"""
    conn = Database.get_connection()
    conn.execute("DELETE FROM part_specifications WHERE part_id=?", (part_id,))
    for i, s in enumerate(specs):
        conn.execute(
            "INSERT INTO part_specifications (part_id, spec_key, spec_value, sort_order) VALUES (?,?,?,?)",
            (part_id, s["spec_key"], s["spec_value"], i)
        )
    conn.commit()


def save_machineries(part_id: int, machinery_list: list):
    """machinery_list: [{"machinery_id": int, "model_note": str}, ...]"""
    conn = Database.get_connection()
    conn.execute("DELETE FROM part_machinery WHERE part_id=?", (part_id,))
    for m in machinery_list:
        conn.execute(
            "INSERT INTO part_machinery (part_id, machinery_id, model_note) VALUES (?,?,?)",
            (part_id, m["machinery_id"], m.get("model_note", ""))
        )
    conn.commit()


def add_relation(part_id_a: int, part_id_b: int, relation_type: str, note: str = ""):
    conn = Database.get_connection()
    # 중복 방지
    exists = conn.execute("""
        SELECT id FROM part_relations
        WHERE (part_id_a=? AND part_id_b=?) OR (part_id_a=? AND part_id_b=?)
    """, (part_id_a, part_id_b, part_id_b, part_id_a)).fetchone()
    if not exists:
        conn.execute(
            "INSERT INTO part_relations (part_id_a, part_id_b, relation_type, note) VALUES (?,?,?,?)",
            (part_id_a, part_id_b, relation_type, note)
        )
        conn.commit()


def delete_relation(relation_id: int):
    conn = Database.get_connection()
    conn.execute("DELETE FROM part_relations WHERE id=?", (relation_id,))
    conn.commit()
