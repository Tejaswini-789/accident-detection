"""
database/schema.py - SQL table definitions
"""

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT DEFAULT 'user',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login    DATETIME
);
"""

CREATE_ACCIDENT_RECORDS = """
CREATE TABLE IF NOT EXISTS accident_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER,
    source_name     TEXT,
    source_type     TEXT,          -- image | video | webcam | cctv
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence      REAL,
    severity        TEXT DEFAULT 'Unknown',
    snapshot_path   TEXT,
    class_label     TEXT,
    bbox_x1         REAL, bbox_y1 REAL, bbox_x2 REAL, bbox_y2 REAL,
    notified        INTEGER DEFAULT 0,
    user_id         INTEGER,
    FOREIGN KEY (session_id) REFERENCES detection_sessions(id),
    FOREIGN KEY (user_id)    REFERENCES users(id)
);
"""

CREATE_DETECTION_SESSIONS = """
CREATE TABLE IF NOT EXISTS detection_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER,
    source_name   TEXT,
    source_type   TEXT,
    start_time    DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time      DATETIME,
    total_frames  INTEGER DEFAULT 0,
    accidents_found INTEGER DEFAULT 0,
    status        TEXT DEFAULT 'running',
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

CREATE_NOTIFICATIONS = """
CREATE TABLE IF NOT EXISTS notifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    accident_id     INTEGER,
    sent_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    recipient_email TEXT,
    status          TEXT,          -- sent | failed
    error_message   TEXT,
    FOREIGN KEY (accident_id) REFERENCES accident_records(id)
);
"""

CREATE_CAMERA_SOURCES = """
CREATE TABLE IF NOT EXISTS camera_sources (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    name        TEXT,
    url         TEXT,
    location    TEXT,
    active      INTEGER DEFAULT 1,
    added_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

ALL_TABLES = [
    CREATE_USERS,
    CREATE_ACCIDENT_RECORDS,
    CREATE_DETECTION_SESSIONS,
    CREATE_NOTIFICATIONS,
    CREATE_CAMERA_SOURCES,
]
