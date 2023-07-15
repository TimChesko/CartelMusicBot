from aiogram import Router

from src.dialogs.admin import dashboard, menu

router = Router()

router.include_routers(dashboard.router, menu.admin_main)
