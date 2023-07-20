from aiogram import Router

from src.dialogs.admin.dashboard.employee import add, menu

router = Router()

router.include_routers(add.new_employee, menu.employees)