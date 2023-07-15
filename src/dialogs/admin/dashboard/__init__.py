from aiogram import Router

from src.dialogs.admin.dashboard import menu, PIN, employee

router = Router()

router.include_routers(PIN.code, menu.admin_main, employee.router)
