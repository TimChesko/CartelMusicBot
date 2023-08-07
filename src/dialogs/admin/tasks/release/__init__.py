from aiogram import Router

from src.dialogs.admin.tasks.release import menu, level1

router = Router()

router.include_routers(menu.main, level1.choose)
