from aiogram import Router
from . import view_status

router = Router()
router.include_router(view_status.dialog)
