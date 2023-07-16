from aiogram import Router

from . import bank, passport, social

router = Router()
router.include_router(bank.add_full_data)
router.include_router(passport.add_full_data)
router.include_router(social.dialog)
