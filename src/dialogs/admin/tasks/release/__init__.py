from aiogram import Router

from src.dialogs.admin.tasks.release import menu, level1, level2, level3

router = Router()

router.include_routers(menu.main, level1.choose, level2.choose, level3.choose)
