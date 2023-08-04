from aiogram import Router
from . import menu, view_info

router = Router()
router.include_router(menu.dialog)
router.include_router(view_info.dialog)
