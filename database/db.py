"""
database/db.py - SQLite connection + helper functions
"""
import sqlite3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import DB_PATH
from database.schema import ALL_TABLES


# ─── Initialise ───────────────────────────────────────────────────────────────
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't already exist."""
    conn = get_connection()
    cur = conn.cursor()
    for ddl in ALL_TABLES:
        cur.execute(ddl)
    conn.commit()
    conn.close()


# ─── Users ────────────────────────────────────────────────────────────────────
def create_user(username: str, email: str, password_hash: str):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?,?,?)",
            (username, email, password_hash),
        )
        conn.commit()
        return True, "User created"
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()


def get_user_by_username(username: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_last_login(user_id: int):
    conn = get_connection()
    conn.execute("UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


# ─── Sessions ─────────────────────────────────────────────────────────────────
def start_session(user_id: int, source_name: str, source_type: str) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO detection_sessions (user_id, source_name, source_type) VALUES (?,?,?)",
        (user_id, source_name, source_type),
    )
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid


def end_session(session_id: int, total_frames: int, accidents_found: int):
    conn = get_connection()
    conn.execute(
        """UPDATE detection_sessions
           SET end_time=CURRENT_TIMESTAMP, total_frames=?, accidents_found=?, status='done'
           WHERE id=?""",
        (total_frames, accidents_found, session_id),
    )
    conn.commit()
    conn.close()


def get_session_stats(user_id: int) -> dict:
    conn = get_connection()
    row = conn.execute(
        """SELECT COUNT(*) as total_sessions,
                  SUM(total_frames) as total_frames,
                  SUM(accidents_found) as total_accidents
           FROM detection_sessions WHERE user_id=?""",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else {}


# ─── Accident Records ─────────────────────────────────────────────────────────
def save_accident(
    session_id, source_name, source_type, confidence,
    severity, snapshot_path, class_label, bbox, user_id
):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO accident_records
           (session_id, source_name, source_type, confidence, severity,
            snapshot_path, class_label, bbox_x1, bbox_y1, bbox_x2, bbox_y2, user_id)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (session_id, source_name, source_type, confidence, severity,
         snapshot_path, class_label, *bbox, user_id),
    )
    record_id = cur.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_accidents(user_id: int, limit: int = 500):
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM accident_records WHERE user_id=?
           ORDER BY timestamp DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_notified(accident_id: int):
    conn = get_connection()
    conn.execute("UPDATE accident_records SET notified=1 WHERE id=?", (accident_id,))
    conn.commit()
    conn.close()


def get_severity_counts(user_id: int) -> dict:
    conn = get_connection()
    rows = conn.execute(
        """SELECT severity, COUNT(*) as cnt FROM accident_records
           WHERE user_id=? GROUP BY severity""",
        (user_id,),
    ).fetchall()
    conn.close()
    return {r["severity"]: r["cnt"] for r in rows}


def get_daily_counts(user_id: int, days: int = 30):
    conn = get_connection()
    rows = conn.execute(
        """SELECT DATE(timestamp) as day, COUNT(*) as cnt
           FROM accident_records WHERE user_id=?
             AND timestamp >= DATE('now', ?)
           GROUP BY day ORDER BY day""",
        (user_id, f"-{days} days"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Notifications ────────────────────────────────────────────────────────────
def save_notification(accident_id: int, recipient: str, status: str, error: str = None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO notifications (accident_id, recipient_email, status, error_message)
           VALUES (?,?,?,?)""",
        (accident_id, recipient, status, error),
    )
    conn.commit()
    conn.close()


# ─── Camera Sources ───────────────────────────────────────────────────────────
def save_camera(user_id: int, name: str, url: str, location: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO camera_sources (user_id, name, url, location) VALUES (?,?,?,?)",
        (user_id, name, url, location),
    )
    conn.commit()
    conn.close()


def get_cameras(user_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM camera_sources WHERE user_id=? AND active=1", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
