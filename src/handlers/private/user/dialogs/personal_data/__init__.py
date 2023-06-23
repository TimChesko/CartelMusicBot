from aiogram import Router

from src.handlers.private.user.dialogs.personal_data import filling_data

router = Router()
router.include_router(filling_data.filling_data)