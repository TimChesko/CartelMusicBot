from aiogram import Router

from src.dialogs.admin import dashboard, MAIN, registration, listening

router = Router()

router.include_routers(dashboard.router, MAIN.menu, registration.reg_fullname, listening.router)
