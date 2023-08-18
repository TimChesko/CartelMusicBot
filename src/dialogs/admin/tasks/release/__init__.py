from aiogram import Router

from src.dialogs.admin.tasks.release import menu, levels

router = Router()

router.include_routers(menu.main, levels.lvl1, levels.lvl2, levels.lvl3)
