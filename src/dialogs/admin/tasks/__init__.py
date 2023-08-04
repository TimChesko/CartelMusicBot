from aiogram import Router
from . import menu, tracks, personal_data, listening, release

router = Router()
router.include_router(menu.dialog)
router.include_router(tracks.router)
router.include_router(personal_data.router)
router.include_router(listening.router)
router.include_router(release.router)
