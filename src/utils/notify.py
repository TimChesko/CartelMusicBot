from aiogram import Dispatcher, Bot

from src.data.config import Config


async def notify_admins(dp: Dispatcher, bot: Bot, config: Config, msg_text: str):
    if config.constant.logging_level == 20:
        for admin in config.constant.developers:
            await bot.send_message(chat_id=admin, text=msg_text)
        dp['aiogram_logger'].info("Admins alert")
    else:
        dp['aiogram_logger'].debug("Admins no alert")
