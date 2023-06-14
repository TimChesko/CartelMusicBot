from aiogram import Router

from . import start, test, dialogs

router = Router()
router.include_router(start.router)
router.include_router(dialogs.router)
# router.include_router(test.router)
# router.include_router(test.dialog)
