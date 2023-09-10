import sqlite3
import aiosqlite
import asyncio
from src.db.schema import insert_data_genre
from src.main import get_response, get_ranges, create_workers
from src._logger import Logger
from src._locations import Directories
from bs4 import BeautifulSoup

MAIN_DIR = Directories.MAIN_DIR
DB = Directories.DB_DIR.joinpath(Directories.ENV_VALUES["DB_NAME"])
Logger().basic_logger


async def parse_html_genre(m_code: int) -> list[str]:
    response, url = await get_response(m_code)
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
            "SELECT title, url_int FROM main WHERE (url_int BETWEEN ? AND ?)",
            (idx_lower, idx_upper),
        ) as cursor:
            async for title, idx in cursor:
                genres = await parse_html_genre(idx)
                if genres is not None:
                    data.append(
                        {"title": title, "url_int": idx, "genre": " ".join(genres)}
                    )
                    await insert_data_genre(data)  # inserts to a sqlite3 database
                    data.clear()


async def automatic_ranges(min_id: int, max_id: int, _type: str):
    print(min_id, max_id)
    workers = int(input("No. of workers: "))
    rg = await get_ranges(min_id, max_id, workers)
    await create_workers(genre_scraper, rg, _type)


async def manual_ranges(_type: str):
    lower = int(input("lower_limit: "))
    upper = int(input("upper limit: "))
    print(lower, upper)
    print(f"lower bound is set to: {lower}")
    print(f"upper bound is set to: {upper}")
    workers = int(input("No. of workers: "))
    rg = await get_ranges(lower, upper, workers)
    await create_workers(genre_scraper, rg, _type)


async def genre():
    _type = "genre"
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    yes = ("y", "Y")
    auto_range = True if input("Automatically set ranges (y/n)? ") in yes else False
    max_id = next(id[0] for id in cursor.execute("SELECT MAX(url_int) FROM main"))
    min_id = next(id[0] for id in cursor.execute("SELECT MAX(url_int) FROM genre"))
    if not min_id:
        min_id = 0
    if auto_range:
        await automatic_ranges(min_id, max_id, _type)
    else:
        await manual_ranges(_type)


if __name__ == "__main__":
    with asyncio.Runner() as runner:
        runner.run(genre())
