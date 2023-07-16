from aiogram import Router

from . import registrations, tracks, start, profile, listening, admin, utils

router = Router()
router.include_router(admin.router)
router.include_router(start.start_menu)
router.include_router(registrations.router)
router.include_router(tracks.router)
router.include_router(profile.router)
router.include_router(listening.router)
router.include_router(utils.router)
