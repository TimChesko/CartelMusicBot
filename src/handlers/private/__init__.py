from aiogram import Router, F

from . import user, privilege

router = Router()
router.message.filter(
    F.chat.type == "private"
)
router.include_routers(user.router)
