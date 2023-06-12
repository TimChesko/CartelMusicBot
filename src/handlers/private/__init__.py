from aiogram import Router, F
from . import admin
from .import user

router = Router()

router.message.filter(F.chat.type == "private")

router.include_router(admin.router)
router.include_router(user.router)