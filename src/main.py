import asyncio

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis
from src import utils
from src.data import config
from src.database.process import DatabaseEngine, AsyncDatabaseManager
from src import handlers
from src.service.diologs_collector import DialogsCollector
from src.utils.notify import notify_admins


async def set_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.router)


async def set_middlewares() -> None:
    pass


async def set_dialogs(dp: Dispatcher):
    dp['dialogs_collector'].include_dialog(handlers.collector)
    dp['aiogram_logger'].debug(f"Test dialogs collector: {dp['dialogs_collector']}")


async def set_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger_init"] = {"type": "aiogram"}
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(**dp["aiogram_logger_init"])
    dp["business_logger_init"] = {"type": "business"}
    dp["business_logger"] = utils.logging.setup_logger().bind(**dp["business_logger_init"])
    dp["database_logger_init"] = {"type": "database"}
    dp["database_logger"] = utils.logging.setup_logger().bind(**dp["database_logger_init"])


async def setup_aiogram(dp: Dispatcher) -> None:
    await set_logging(dp)
    logger = dp["aiogram_logger"]
    logger.info("Configuring aiogram")
    await set_handlers(dp)
    await set_middlewares()
    await set_dialogs(dp)
    logger.info("Configured aiogram")


async def set_database(dp: Dispatcher) -> None:
    dp['engine'] = await DatabaseEngine.connect(config)
    # await AsyncDatabaseManager(dp['engine'], dp['database_logger']).create_tables()


async def on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher)
    await set_database(dispatcher)
    await notify_admins(dispatcher, "Бот запущен")
    dispatcher["aiogram_logger"].info("Started polling")


async def on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await DatabaseEngine.close_connection(dispatcher['engine'])
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
            )
        )
    )

    dp['config'] = config
    dp['bot'] = bot
    dp['dialogs_collector'] = DialogsCollector()

    dp.startup.register(on_startup_polling)
    dp.shutdown.register(on_shutdown_polling)
    await dp.start_polling(bot)


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
