from aiogram import Router

from src.dialogs.admin.listening import tracklist

router = Router()

router.include_router(tracklist.tracks)
