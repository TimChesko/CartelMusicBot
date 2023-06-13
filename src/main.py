import asyncio

from aiogram import Dispatcher, Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from redis.asyncio.client import Redis

from src import handlers
from src import utils
from src.data import config
from src.database.process import DatabaseManager
from src.middlewares.ban import CheckBan
from src.middlewares.throttling import ThrottlingMiddleware
from src.utils.notify import notify_admins


async def set_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.router)


async def set_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware(CheckBan())
    dp.message.middleware(ThrottlingMiddleware(storage=dp.storage))


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
    setup_dialogs(dp)
    dp["aiogram_logger"].info("Configured aiogram")


async def set_database(dp: Dispatcher) -> None:
    dp['engine'] = await DatabaseManager.connect(dp['config'])
    await DatabaseManager.create_tables(dp['engine'])


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
    dp = Dispatcher(
        storage=RedisStorage(
            redis=Redis(
                host=config.FSM_HOST,
                password=None,
                port=config.FSM_PORT,
                db=0,
            ),
            key_builder=DefaultKeyBuilder(with_destiny=True)
        )
    )

    dp['config'] = config
    dp['bot'] = bot

    dp.startup.register(on_startup_polling)
    dp.shutdown.register(on_shutdown_polling)
    await dp.start_polling(bot)


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
