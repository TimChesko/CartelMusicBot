from aiogram import Router

from . import nickname

router = Router()
router.include_router(nickname.reg_nickname)
