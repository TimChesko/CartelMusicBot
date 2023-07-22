import asyncio

from aiogram import Dispatcher, Bot
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from redis.asyncio.client import Redis

from src import handlers, dialogs
from src import utils
from src.data import config
from src.database.process import DatabaseManager
from src.dialogs.utils.common import on_unknown_intent, on_unknown_state
from src.middlewares.ban import CheckBan
from src.middlewares.employee import EmployeeCheck
from src.middlewares.throttling import ThrottlingMiddleware
from src.utils.notify import notify_admins


async def set_dialogs(dp: Dispatcher) -> None:
    dp.include_router(dialogs.router)
    setup_dialogs(dp)


async def set_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.router)


async def set_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware(CheckBan())
    dp.message.middleware(ThrottlingMiddleware(storage=dp.storage))
    dp.message.middleware(EmployeeCheck())


async def set_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger_init"] = {"type": "aiogram"}
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(**dp["aiogram_logger_init"])
    dp["business_logger_init"] = {"type": "business"}
    dp["business_logger"] = utils.logging.setup_logger().bind(**dp["business_logger_init"])
    dp["database_logger_init"] = {"type": "database"}
    dp["database_logger"] = utils.logging.setup_logger().bind(**dp["database_logger_init"])


async def setup_aiogram(dp: Dispatcher) -> None:
    await set_logging(dp)

    dp["aiogram_logger"].info("Configuring aiogram")
    await set_middlewares(dp)
    await set_handlers(dp)
    await set_dialogs(dp)
    dp["aiogram_logger"].info("Configured aiogram")


async def set_database(dp: Dispatcher) -> None:
    dp['engine'] = await DatabaseManager.create_engine(dp['config'])
    dp['session_maker'] = await DatabaseManager.create_session_maker(dp['engine'])


async def on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher)
    await set_database(dispatcher)
    await notify_admins(dispatcher, "Бот запущен")
    dispatcher["aiogram_logger"].info("Started polling")


async def on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await dispatcher['engine'].close()
    await notify_admins(dispatcher, "Бот выключен")
    await bot.session.close()
    dispatcher["aiogram_logger"].info("Stopping polling")


async def main() -> None:
    bot = Bot(config.BOT_TOKEN, parse_mode="HTML")
    storage = RedisStorage(
        redis=Redis(
            host=config.FSM_HOST,
            password=config.FSM_PASSWORD,
            port=config.FSM_PORT,
            db=0,
        ),
        key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    dp = Dispatcher(
        storage=storage,
        events_isolation=storage.create_isolation()
    )

    dp['config'] = config
    dp['bot'] = bot
    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.errors.register(
        on_unknown_state,
        ExceptionTypeFilter(UnknownState),
    )
    dp.startup.register(on_startup_polling)
    dp.shutdown.register(on_shutdown_polling)
    await dp.start_polling(bot)


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
