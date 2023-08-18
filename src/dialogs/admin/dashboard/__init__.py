from aiogram import Router

from src.dialogs.admin.dashboard import employee, main, templates

router = Router()

router.include_routers(main.dashboard, employee.router, templates.router)
