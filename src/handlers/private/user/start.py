import asyncio

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.service.diologs_collector import DialogsCollector

router = Router()

dialogs = DialogsCollector()
dialogs.include_dialogs(123, "124")
dialogs.include_dialog("TEST")


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message):
    await asyncio.sleep(5)
    await msg.answer("Привет")
