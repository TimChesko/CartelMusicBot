from aiogram import Router
from . import view_status, form_track, edit_data

router = Router()
router.include_router(view_status.dialog)
router.include_router(form_track.dialog)
router.include_router(edit_data.dialog)
