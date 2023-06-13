from aiogram import Router

from . import start, test

router = Router()
router.include_router(test.router)
router.include_router(test.dialog)
