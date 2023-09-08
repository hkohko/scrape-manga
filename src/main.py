import httpx
import asyncio
from asyncio import create_task
import logging
import sqlite3
from src._logger import Logger
from src.db.schema import insert_data
from src._locations import Directories
from bs4 import BeautifulSoup

MAIN_DIR = Directories.MAIN_DIR
DB = Directories.DB_DIR.joinpath(Directories.ENV_VALUES["DB_NAME"])
Logger().basic_logger

codes = {1: 54256, 2: 1}


async def get_response(m_code: int):
    BASE_URL: str = Directories.ENV_VALUES["BASE_URL"] + str(m_code)
    while True:
        try:
            async with httpx.AsyncClient() as aioclient:
                r = await aioclient.get(BASE_URL)
            return r, BASE_URL
        except httpx.HTTPError:
            logging.warning("Encountered httpx.HTTPERROR")
            for i in range(0, 60):
                print(f"will retry in {60-i}s", end=" \r")
                await asyncio.sleep(1)
            continue


async def parse_html(m_code: int):
    response, url = await get_response(m_code)
    soup = BeautifulSoup(response, "lxml")
    main_tree = soup.find("main")
    h3 = main_tree.find("h3", {"class": "text-2xl font-bold"})
    if h3 is None:
        return None, None
    manga_title = h3.find("a", {"href": True, "class": "link link-hover"})
    return manga_title.text, url


async def start_scraping(idx_lower: int, idx_upper: int):
    data = []
    for idx in range(idx_lower, idx_upper):
        # parse_html => beautifulsoup scrapes html, response from httpx.asyncclient()
        title, url = await parse_html(idx)
        data.append({"url_int": idx, "title": title, "link": url})
        insert_data(data)  # inserts to a sqlite3 database
        data.clear()


async def get_range(upper: int, workers: int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(url_int) FROM main")
    for max_url_int in cursor:
        if max_url_int[0] is None:
            start_from = 1
        else:
            start_from = max_url_int[0]
    if upper < start_from:
        raise ValueError(f"Lowest entry must be bigger than {start_from}")

    scrape_range = upper - start_from
    distribution = scrape_range // workers
    dist_list = []
    for idx in range(workers):
        dist_list.append(start_from + (distribution * (idx + 1)))
    dist_list[-1] = upper
    return dist_list


async def create_workers(dist_list: list):
    queue_workers = []
    for idx, _ in enumerate(dist_list):
        if idx + 1 == len(dist_list):
            break
        queue_workers.append(
            create_task(start_scraping(dist_list[idx], dist_list[idx + 1]))
        )
    await asyncio.gather(*queue_workers)


if __name__ == "__main__":
    entry = int(input("upper limit: "))
    workers = int(input("No. of workers: "))
    with asyncio.Runner() as runner:
        rg = runner.run(get_range(entry, workers))
        runner.run(create_workers(rg))
