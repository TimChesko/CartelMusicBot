from aiogram import Router

from . import confirm, view

router = Router()
router.include_router(view.router)
router.include_router(confirm.confirm_personal_data)
