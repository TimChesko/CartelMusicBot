from aiogram import Dispatcher

from src.data.config import Config


async def notify_admins(dp: Dispatcher, msg_text: str):
    config_app: Config = dp['retort'].load(dp['config'], Config)
    if config_app.app.logging_level == 20:
        for admin in config_app.app.developers:
            await dp['bot'].send_message(chat_id=admin, text=msg_text)
        dp['aiogram_logger'].info("Admins alert")
    else:
        dp['aiogram_logger'].debug("Admins no alert")
