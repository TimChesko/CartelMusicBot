from aiogram import Router
from . import registrations, tracks

router = Router()
router.include_router(registrations.router)
router.include_router(tracks.router)
