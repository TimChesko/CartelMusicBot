from aiogram import Router
from . import registrations, tracks, start

router = Router()
router.include_router(registrations.router)
router.include_router(tracks.router)
router.include_router(start.start_menu)
