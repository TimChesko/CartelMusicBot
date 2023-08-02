from aiogram import Router

from src.dialogs.my_studio.release import create, page, tracks

router = Router()

router.include_routers(create.main, page.main, tracks.choose_track)
