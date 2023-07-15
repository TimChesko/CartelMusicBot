from aiogram import Router

from src.handlers.private.privilege.moderator import menu

router = Router()

router.include_router(menu.router)