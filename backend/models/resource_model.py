from database.db import get_db_connection

class Resource:
    @staticmethod
    def save(user_id, title, link, r_type, platform, description):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO resources (user_id, title, link, type, platform, description) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, title, link, r_type, platform, description)
            )
            resource_id = cur.lastrowid
            conn.commit()
            return resource_id
        except Exception as e:
            print(f"Error saving resource: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_user(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM resources WHERE user_id = ? ORDER BY saved_at DESC", (user_id,))
        rows = cur.fetchall()
        conn.close()
        # Convert sqlite3.Row to plain dicts for JSON serialisation
        return [dict(r) for r in rows]

    @staticmethod
    def delete_by_link(user_id, link):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "DELETE FROM resources WHERE user_id = ? AND link = ?",
                (user_id, link)
            )
            deleted = cur.rowcount > 0
            conn.commit()
            return deleted
        except Exception as e:
            print(f"Error deleting resource: {e}")
            return False
        finally:
            conn.close()
