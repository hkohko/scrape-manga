import httpx
import asyncio
from src._locations import Directories
from bs4 import BeautifulSoup

MAIN_DIR = Directories.MAIN_DIR
RESP_DIR = MAIN_DIR.joinpath("sample_resp")


async def get_response(m_code: int):
    BASE_URL: str = Directories.ENV_VALUES["BASE_URL"] + str(m_code)
    while True:
        try:
            async with httpx.AsyncClient() as aioclient:
                r = await aioclient.get(BASE_URL)
            return r, BASE_URL
        except httpx.HTTPError:
            for i in range(0, 60):
                print(f"httpx.HTTPERROR, will retry in {60-i}s", end=" \r")
                asyncio.sleep(1)
            continue          



async def parse_html(m_code: int):
    response, url = await get_response(m_code)
    soup = BeautifulSoup(response, "lxml")
    main_tree = soup.find("main")
    h3 = main_tree.find("h3", {"class": "text-2xl font-bold"})
    if h3 is None:
        return "dead link", "dead url"
    manga_title = h3.find("a", {"href": True, "class": "link link-hover"})
    return manga_title.text, url


if __name__ == "__main__":
    with asyncio.Runner() as runner:
        for idx in range(1, 10):
            title, url = runner.run(parse_html(idx))