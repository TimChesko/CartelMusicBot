from dataclasses import dataclass
from typing import List

from environs import Env


@dataclass
class TgBot:
    token: str
    webhook_url: str


@dataclass
class Postgres:
    host: str
    user: str
    password: str
    database: str


@dataclass
class RedisServer:
    host: str
    port: int
    password: str = None


@dataclass
class Constant:
    developers: List[int]
    privileges: List[str]
    chats_backup: List[int]
    logging_level: int
    support: str


@dataclass
class Config:
    tg: TgBot
    postgres: Postgres
    redis: RedisServer
    constant: Constant


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg=TgBot(
            token=env.str("BOT_TOKEN"),
            webhook_url=env.str("WEBHOOK_URL")
        ),
        postgres=Postgres(
            host=env.str("PG_HOST"),
            user=env.str("PG_USER"),
            password=env.str("PG_PASSWORD"),
            database=env.str("PG_DATABASE")
        ),
        redis=RedisServer(
            host=env.str("FSM_HOST"),
            port=env.int("FSM_PORT"),
            password=env.str("FSM_PASSWORD")
        ),
        constant=Constant(
            developers=list(map(int, env.list("DEVELOPERS"))),
            privileges=list(map(str, env.list("PRIVILEGES"))),
            chats_backup=list(map(int, env.list("CHATS_BACKUP"))),
            logging_level=env.int("LOGGING_LEVEL"),
            support="@CartelMusicSupport"
        )
    )
