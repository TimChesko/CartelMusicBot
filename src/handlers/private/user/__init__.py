from aiogram import Router

from . import start, test, registration

router = Router()
router.include_router(start.router)
router.include_router(registration.router)
# router.include_router(test.router)
# router.include_router(test.dialog)
