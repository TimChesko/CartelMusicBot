from aiogram import Router

from . import private

router = Router()

router.include_router(private.router)
