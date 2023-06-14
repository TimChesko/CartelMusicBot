from aiogram import Router
from . import registrations

router = Router()
router.include_router(registrations.router)
