from aiogram import Router
from . import view_public

router = Router()
router.include_router(view_public.dialog)
