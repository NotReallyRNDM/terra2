import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "polls.db"

def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    schema_path = BASE_DIR / "sql.sql"

    with get_db() as db:
        db.executescript(
            schema_path.read_text(encoding="utf-8")
        )




if __name__ == "__main__":
    init_db()
    print("database initialised!")





