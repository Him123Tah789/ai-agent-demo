import sqlite3

DB_PATH = "agent_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            agent_type TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_memory(session_id, agent_type, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memory (session_id, agent_type, message) VALUES (?, ?, ?)",
        (session_id, agent_type, message)
    )
    conn.commit()
    conn.close()


def load_memory(session_id, limit=3):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT agent_type, message FROM memory WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows[::-1]  # oldest → newest
