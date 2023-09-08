import httpx
import asyncio
import logging
from src._logger import Logger
from src.db.schema import insert_data
from src._locations import Directories
from bs4 import BeautifulSoup

MAIN_DIR = Directories.MAIN_DIR
RESP_DIR = MAIN_DIR.joinpath("sample_resp")
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
                asyncio.sleep(1)
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


async def store_data(idx: int):
    data = []
    title, url = await parse_html(idx)
    if title is not None and url is not None:
        data.append({"url_int": idx, "title": title, "link": url})
        insert_data(data)
        data.clear()
    else:
        logging.info("dead link and url")


if __name__ == "__main__":
    with asyncio.Runner() as runner:
        # for idx in range(1, 10):
        runner.run(store_data(codes.get(1)))
