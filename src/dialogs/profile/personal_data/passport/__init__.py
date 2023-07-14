from aiogram import Router

from . import data_filler, edit, input_factory

router = Router()
router.include_router(data_filler.passport)
router.include_router(edit.dialog)
router.include_router(input_factory.dialog_input_text)
