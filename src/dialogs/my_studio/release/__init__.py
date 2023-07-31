from aiogram import Router

from src.dialogs.my_studio.release import create_album

router = Router()

router.include_router(create_album.main)
