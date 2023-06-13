from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message):
    await msg.answer(msg.json())
    await msg.answer("Привет")
