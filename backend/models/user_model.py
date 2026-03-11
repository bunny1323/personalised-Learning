from database.db import get_db_connection
import bcrypt
from datetime import date

class User:
    @staticmethod
    def create(name, email, password):
        conn = get_db_connection()
        cur = conn.cursor()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            user_id = cur.lastrowid
            conn.commit()
            return {"id": user_id, "name": name, "email": email}
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def find_by_email(email):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()
        return user

    @staticmethod
    def update_learning_style(user_id, style):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET learning_style = ? WHERE id = ?", (style, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_streak(user_id):
        """Increments daily streak, resets if more than 1 day has passed."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT streak_count, last_login FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            if not row:
                return 0

            today = date.today()
            last_login_str = row['last_login']
            streak = row['streak_count'] or 0

            if last_login_str is None:
                streak = 1
            else:
                last_login = date.fromisoformat(last_login_str)
                days_diff = (today - last_login).days
                if days_diff == 1:
                    streak += 1
                elif days_diff == 0:
                    pass  # Same day — no change
                else:
                    streak = 1  # Gap, reset

            cur.execute(
                "UPDATE users SET streak_count = ?, last_login = ? WHERE id = ?",
                (streak, today.isoformat(), user_id)
            )
            conn.commit()
            return streak
        except Exception as e:
            print(f"Streak update error: {e}")
            return 0
        finally:
            conn.close()
