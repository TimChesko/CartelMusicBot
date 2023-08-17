from aiogram import Router

from . import start, get_id, bot_info

router = Router()

router.include_router(start.router)
router.include_router(get_id.router)
router.include_router(bot_info.router)
