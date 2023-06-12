from aiogram import Dispatcher

from src.data import config


async def notify_admins(dp: Dispatcher, msg_text: str):
    if dp['config'].LOGGING_LEVEL == 20:
        for admin in config.ADMINS:
            await dp['bot'].send_message(chat_id=admin, text=msg_text)
        dp['aiogram_logger'].info("Admins alert")
    else:
        dp['aiogram_logger'].debug("Admins no alert")
