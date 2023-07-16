from aiogram import Router

from . import input_forms

router = Router()
router.include_router(input_forms.router)
