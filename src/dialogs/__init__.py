from aiogram import Router

from . import registrations, tracks, start, profile

router = Router()
router.include_router(registrations.router)
router.include_router(tracks.router)
router.include_router(start.start_menu)
router.include_router(profile.router)
