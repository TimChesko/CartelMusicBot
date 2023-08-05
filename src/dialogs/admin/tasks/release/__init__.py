from aiogram import Router

from src.dialogs.admin.tasks.release import menu, level

router = Router()

router.include_routers(menu.main, level.choose)
