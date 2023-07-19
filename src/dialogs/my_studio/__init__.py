from aiogram import Router
from . import my_tracks, public, menu

router = Router()
router.include_router(my_tracks.router)
router.include_router(public.router)
router.include_router(menu.dialog)
