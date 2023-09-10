import sqlite3
import logging
import aiosqlite
from pathlib import PurePath
from src._logger import Logger
from src._locations import Directories

Logger().basic_logger


def create_tables_main(conn: sqlite3.Connection):
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


def create_tables_genre(conn: sqlite3.Connection):
    cursor = conn.cursor()
    Q_CREATE_TABLE_GENRE = """CREATE TABLE IF NOT EXISTS genre(
    url_int INTEGER,
    title TEXT,
    genres TEXT,
    FOREIGN KEY(url_int) REFERENCES main(url_int)
    )
    STRICT
    """
    cursor.execute(Q_CREATE_TABLE_GENRE)
    cursor.execute("PRAGMA journal_mode=wal")


async def insert_data(DB: PurePath, data: list):
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
    while True:
        try:
            async with aiosqlite.connect(DB) as conn:
                async with conn.executemany(Q_INSERT_INTO_MAIN, data):
                    await conn.commit()
            break
        except sqlite3.OperationalError:
            continue
    title = data[0].get("title")
    idx = data[0].get("url_int")
    logging.info(f"commited entry {idx}: {title}")


async def insert_data_genre(DB: PurePath, data: list):
    Q_INSERT_INTO_GENRE = """INSERT OR IGNORE INTO genre(
    url_int,
    title,
    genres
    ) VALUES(
    :url_int,
    :title,
    :genre
    )
    """
    # TODO: rewrite to pass around one database connection is needed
    # ^becomes very slow
    while True:
        try:
            async with aiosqlite.connect(DB) as conn:
                async with conn.executemany(Q_INSERT_INTO_GENRE, data):
                    await conn.commit()
            break
        except sqlite3.OperationalError:
            continue
    thedict = data[0]
    idx = thedict.get("url_int")
    genres = thedict.get("genre")
    logging.info(f"commited genre {idx}: {genres}")


if __name__ == "__main__":
    # DB = Directories.DB_DIR.joinpath(Directories.ENV_VALUES["DB_PROTO"])
    # create_tables_genre(sqlite3.connect(DB))
    # create_tables_main(sqlite3.connect(DB))
    pass
