from aiogram import Router

from . import edit, input_factory, process, utils

router = Router()
router.include_router(edit.dialog)
router.include_router(input_factory.dialog_input_text)
