from pathlib import PurePath
from dataclasses import dataclass
from dotenv import dotenv_values

@dataclass()
class Directories:
    PROJ_DIR = PurePath(__file__).parents[1]
    MAIN_DIR = PROJ_DIR.joinpath("src")
    RESP_DIR = MAIN_DIR.joinpath("sample_resp")
    DB_DIR = MAIN_DIR.joinpath("db", "sqlite3_db")
    ENV_VALUES = dotenv_values(f"{PROJ_DIR}/.env")