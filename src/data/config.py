from environs import Env


env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")
DEVELOPERS: list = list(map(int, env.list("DEVELOPERS")))
# =234234,234234,234234
PRIVILEGES: list = list(map(str, env.list("PRIVILEGES")))
LOGGING_LEVEL: int = env.int("LOGGING_LEVEL")
# INFO - 20, DEBUG - 10, ERROR - 40

PG_HOST: str = env.str("PG_HOST")
PG_USER: str = env.str("PG_USER")
PG_PASSWORD: str = env.str("PG_PASSWORD")
PG_DATABASE: str = env.str("PG_DATABASE")

FSM_HOST: str = env.str("FSM_HOST")
FSM_PORT: int = env.int("FSM_PORT")
FSM_PASSWORD: str = env.str("FSM_PASSWORD")
