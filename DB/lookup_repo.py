from DB.database import Database

def get_all_categories():
    conn = Database.get_connection()
    return conn.execute("SELECT id, name, parent_id FROM categories ORDER BY parent_id NULLS FIRST, name").fetchall()

def get_all_machinery_types():
    conn = Database.get_connection()
    return conn.execute("SELECT id, name FROM machinery_types ORDER BY id").fetchall()

def get_all_manufacturers():
    conn = Database.get_connection()
    return conn.execute("SELECT id, name FROM manufacturers ORDER BY name").fetchall()

def insert_manufacturer(name, country="", contact="", website=""):
    conn = Database.get_connection()
    cur = conn.execute("INSERT INTO manufacturers (name, country, contact, website) VALUES (?,?,?,?)",
                       (name, country, contact, website))
    conn.commit()
    return cur.lastrowid

def update_manufacturer(manufacturer_id, name, country="", contact="", website=""):
    conn = Database.get_connection()
    conn.execute(
        "UPDATE manufacturers SET name=?, country=?, contact=?, website=? WHERE id=?",
        (name, country, contact, website, manufacturer_id)
    )
    conn.commit()

def delete_manufacturer(manufacturer_id):
    conn = Database.get_connection()
    conn.execute("DELETE FROM manufacturers WHERE id=?", (manufacturer_id,))
    conn.commit()

def insert_category(name, parent_id=None, description=""):
    conn = Database.get_connection()
    cur = conn.execute("INSERT INTO categories (name, parent_id, description) VALUES (?,?,?)",
                       (name, parent_id, description))
    conn.commit()
    return cur.lastrowid

def insert_machinery_type(name, description=""):
    conn = Database.get_connection()
    cur = conn.execute("INSERT INTO machinery_types (name, description) VALUES (?,?)", (name, description))
    conn.commit()
    return cur.lastrowid
