from aiogram import Router

from src.handlers.group import listening_approvement

router = Router()

router.include_router(listening_approvement.router)
