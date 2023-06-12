from aiogram import Router
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def cmd_start():
    pass
