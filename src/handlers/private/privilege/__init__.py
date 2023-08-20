from aiogram import Router

from src.filters.employee import EmployeeCheck
from . import moderator, menu

router = Router()

router.message.filter(EmployeeCheck())
router.include_routers(menu.router)
