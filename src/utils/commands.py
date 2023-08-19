from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_start_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="🏠 Главное меню"
        ),
        BotCommand(
            command="info",
            description="🚀 Узнать все возможности бота"
        ),
        BotCommand(
            command="help",
            description="❓ Частые вопросы"
        ),
        BotCommand
    ]
    return await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
