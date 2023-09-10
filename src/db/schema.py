import sqlite3
import logging
import aiosqlite
from src._logger import Logger
from src._locations import Directories

Logger().basic_logger

DB = f"{Directories.DB_DIR}/{Directories.ENV_VALUES['DB_NAME']}"


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
    cursor.execute("PRAGMA journal_mode=wal")


async def insert_data(data: list):
    Q_INSERT_INTO_MAIN = """INSERT OR IGNORE INTO main(
    url_int,
    title,
    link
    ) VALUES(
    :url_int,
    :title,
    :link
    )
    """

    async with aiosqlite.connect(DB) as conn:
        async with conn.executemany(Q_INSERT_INTO_MAIN, data) as _:
            await conn.commit()
    title = data[0].get("title")
    idx = data[0].get("url_int")
    logging.info(f"commited entry {idx}: {title}")


if __name__ == "__main__":
    # create_tables(db_connect())
    pass
