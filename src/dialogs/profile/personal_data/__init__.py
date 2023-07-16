from aiogram import Router

from . import confirm, string, view, process, widget_forms

router = Router()
router.include_router(view.router)
router.include_router(process.router)
router.include_router(confirm.confirm_personal_data)
router.include_router(widget_forms.router)
