from aiogram import Router

from . import my_tracks, menu

router = Router()
router.include_router(my_tracks.router)
router.include_router(menu.dialog)
