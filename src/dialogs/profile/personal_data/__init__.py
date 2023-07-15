from aiogram import Router

from . import confirm, string, view, process

router = Router()
router.include_router(view.router)
router.include_router(process.router)
router.include_router(confirm.confirm_personal_data)
