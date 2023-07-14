from aiogram import Router

from . import data_filler, process, input_factory

router = Router()
router.include_router(data_filler.passport)
router.include_router(process.dialog)

router.include_router(input_factory.dialog_input_text)
router.include_router(input_factory.dialog_input_date)
