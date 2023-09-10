import sqlite3
import aiosqlite
import asyncio
from src.db.schema import insert_data_genre
from src.main import get_response, get_ranges
from src._logger import Logger
from src._locations import Directories
from bs4 import BeautifulSoup

MAIN_DIR = Directories.MAIN_DIR
DB = Directories.DB_DIR.joinpath(Directories.ENV_VALUES["DB_NAME"])
Logger().basic_logger


async def parse_html_genre(m_code: int) -> list[str]:
    response = await get_response(m_code)
    soup = BeautifulSoup(response.text, "lxml")
    try:
        main_tree = soup.find("main")
        div = main_tree.find("div", {"class": "flex items-center flex-wrap"})
        spans = div.find_all("span", {"class": None})
        genres = [span.text for span in spans]
        return genres
    except AttributeError:
        return None


async def genre_scraper(idx_lower: int, idx_upper: int):
    data = []
    async with aiosqlite.connect(DB) as conn:
        async with conn.execute(
            "SELECT url_int FROM main WHERE (url_int BETWEEN ? AND ?)",
            (idx_lower, idx_upper),
        ) as cursor:
            async for idx in cursor:
                genres = await parse_html_genre(idx[0])
                if genres is not None:
                    data.append({"genre": " ".join(genres)})
                    print(data)
                    insert_data_genre(data)  # inserts to a sqlite3 database
                    data.clear()


async def genre(to_scrape: str):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    yes = ("y", "Y")
    auto_range = True if input("Automatically set ranges (y/n)? ") in yes else False
    max_id = next(id[0] for id in cursor.execute("SELECT MAX(url_int) FROM main"))
    min_id = next(id[0] for id in cursor.execute("SELECT MIN(url_int) FROM main"))
    if auto_range:
        await genre_scraper(min_id, max_id)
    else:
        while True:
            upper = int(input("upper limit: "))
            cursor.execute("SELECT * FROM main WHERE url_int=?", (upper,))
            upper_lim = [idx for idx in cursor]
            if len(upper_lim) == 0:
                print(f"No data for manga with id={upper}")
                upper_lim.clear()
                continue
            else:
                await genre_scraper(min_id, upper)
                break


with asyncio.Runner() as runner:
    runner.run(genre("genre"))
