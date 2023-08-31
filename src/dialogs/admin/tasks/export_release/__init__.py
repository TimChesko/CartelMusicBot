from aiogram import Router
from . import windows

router = Router()
router.include_router(windows.export_release)
