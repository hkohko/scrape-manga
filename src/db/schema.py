import sqlite3
from src._locations import Directories


def db_connect() -> sqlite3.Connection:
    return sqlite3.connect(f"{Directories.DB_DIR}/{Directories.ENV_VALUES['DB_NAME']}")


def create_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()
    Q_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS main(
    url_int INTEGER PRIMARY KEY,
    title TEXT,
    link TEXT UNIQUE
    )
    STRICT
    """
    cursor.execute(Q_CREATE_TABLE)


def insert_data(conn: sqlite3.Connection):
    cursor = conn.cursor()


if __name__ == "__main__":
    db_connect()
