from aiogram import Router

from . import my_tracks, menu, release

router = Router()
router.include_router(release.router)
router.include_router(my_tracks.router)
router.include_router(menu.dialog)
