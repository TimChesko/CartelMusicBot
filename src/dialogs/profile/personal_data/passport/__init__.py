from aiogram import Router

from . import passport, edit, input_factory, bank

router = Router()
router.include_router(passport.add_full_data)
router.include_router(edit.dialog)
router.include_router(input_factory.dialog_input_text)

router.include_router(bank.add_full_data)
