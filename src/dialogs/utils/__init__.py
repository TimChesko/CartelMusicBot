from aiogram import Router

from . import widgets

router = Router()
router.include_router(widgets.router)
