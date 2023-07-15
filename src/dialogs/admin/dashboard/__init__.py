from aiogram import Router

from src.dialogs.admin.dashboard import PIN, employee, main

router = Router()

router.include_routers(PIN.code, main.dashboard, employee.router)
