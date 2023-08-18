from aiogram import Router

from src.middlewares.employee import EmployeeCheck
from . import moderator, menu

router = Router()

router.message.filter(EmployeeCheck())
router.include_routers(menu.router)
