from aiogram import Router

from . import data_filler, process

router = Router()
router.include_router(data_filler.passport)
router.include_router(process.dialog)
