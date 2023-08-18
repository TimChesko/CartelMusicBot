from aiogram import Router

from src.dialogs.admin.tasks.listening import tracklist

router = Router()

router.include_router(tracklist.tracks)
