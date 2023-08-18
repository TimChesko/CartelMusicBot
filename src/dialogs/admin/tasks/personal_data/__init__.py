from aiogram import Router

from . import menu, factory

router = Router()
router.include_router(menu.dialog)
router.include_router(factory.router)
