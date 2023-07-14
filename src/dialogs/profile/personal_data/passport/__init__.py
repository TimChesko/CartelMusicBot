from aiogram import Router

from . import add, process

router = Router()
router.include_router(add.passport)
router.include_router(process.dialog)
