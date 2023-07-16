from aiogram import Router

from . import window_input

router = Router()
router.include_router(window_input.dialog_input)
