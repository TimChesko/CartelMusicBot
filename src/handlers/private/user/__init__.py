from aiogram import Router

from . import start, test

router = Router()
router.include_router(start.router)
router.include_router(test.router)
