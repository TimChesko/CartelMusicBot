from aiogram import Router

from src.dialogs.admin import dashboard, menu, registration

router = Router()

router.include_routers(dashboard.router, menu.admin_main, registration.reg_fullname)
