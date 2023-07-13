from aiogram import Router

from . import menu, personal_data

router = Router()
router.include_router(menu.menu)
router.include_router(personal_data.router)
