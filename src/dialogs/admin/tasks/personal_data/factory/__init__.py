from aiogram import Router
from . import window

router = Router()
router.include_router(window.dialog)
