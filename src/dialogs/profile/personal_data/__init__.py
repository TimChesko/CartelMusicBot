from aiogram import Router

from . import confirm, passport, bank, string

router = Router()
router.include_router(passport.router)
router.include_router(confirm.confirm_personal_data)
