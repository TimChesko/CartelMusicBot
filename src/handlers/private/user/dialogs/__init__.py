from aiogram import Router
from . import registrations, tracks, personal_data

router = Router()
router.include_router(registrations.router)
router.include_router(tracks.router)
router.include_router(personal_data.router)