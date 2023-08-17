from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command(commands=["get_id"]), flags={'chat_action': 'typing'})
async def cmd_get_id(msg: Message):
    await msg.delete()
    await msg.answer(f"💠 Ваш <b>telegram id</b>: <code>{msg.from_user.id}</code>")
