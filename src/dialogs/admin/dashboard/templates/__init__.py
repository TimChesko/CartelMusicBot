from aiogram import Router

from src.dialogs.admin.dashboard.templates import listening
from src.dialogs.admin.dashboard.templates import menu

router = Router()

router.include_routers(listening.choice, menu.template_menu)
