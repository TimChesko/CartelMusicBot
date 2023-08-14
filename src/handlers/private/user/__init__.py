from aiogram import Router

from . import start, get_id

router = Router()
router.include_router(start.router)
router.include_router(get_id.router)
