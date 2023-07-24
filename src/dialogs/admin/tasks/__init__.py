from aiogram import Router
from . import menu, tracks, personal_data

router = Router()
router.include_router(menu.dialog)
router.include_router(tracks.router)
router.include_router(personal_data.router)
