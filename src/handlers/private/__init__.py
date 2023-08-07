from aiogram import Router, F

from . import user, privilege

router = Router()
router.message.filter(
    F.chat.type == "private"
)
router.include_router(privilege.router)
router.include_router(user.router)
