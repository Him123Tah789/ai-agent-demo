import sqlite3
from pathlib import Path

# -----------------------------
# Database path (stable)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "agent_data.db"

# -----------------------------
# Get DB connection (thread-safe)
# -----------------------------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# -----------------------------
# Initialize database
# -----------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # Agent Memory Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            agent_type TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    # -----------------------------
    # Document Store Table (NEW)
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            doc_name TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# -----------------------------
# Save agent memory
# -----------------------------
def save_memory(session_id: str, agent_type: str, message: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO memory (session_id, agent_type, message) VALUES (?, ?, ?)",
        (session_id, agent_type, message)
    )

    conn.commit()
    conn.close()

# -----------------------------
# Load recent agent memory
# -----------------------------
def load_memory(session_id: str, limit: int = 3):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT agent_type, message
        FROM memory
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit)
    )

    rows = cursor.fetchall()
    conn.close()

    # Oldest → newest
    return rows[::-1]

# -----------------------------
# Save uploaded document (NEW)
# -----------------------------
def save_document(session_id: str, doc_name: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO documents (session_id, doc_name, content) VALUES (?, ?, ?)",
        (session_id, doc_name, content)
    )

    conn.commit()
    conn.close()

# -----------------------------
# Load documents for session (NEW)
# -----------------------------
def load_documents(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT doc_name, content
        FROM documents
        WHERE session_id = ?
        """,
        (session_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows
