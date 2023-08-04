from aiogram import Router

from src.dialogs.admin.tasks.release import menu

router = Router()

router.include_routers(menu.main)
