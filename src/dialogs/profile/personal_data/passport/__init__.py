from aiogram import Router

from . import add

router = Router()
router.include_router(add.passport)
