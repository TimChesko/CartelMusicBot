from aiogram import Router

from . import start, dialogs

router = Router()
router.include_router(start.router)
router.include_router(dialogs.router)
router.include_router(start.start_menu)
# router.include_router(test.router)
# router.include_router(test.dialog)
