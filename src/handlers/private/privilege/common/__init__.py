from aiogram import Router

from . import privilege

router = Router()

router.include_router(privilege.router)
