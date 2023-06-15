from aiogram import Router
from . import listening

router = Router()
router.include_router(listening.dialog)
