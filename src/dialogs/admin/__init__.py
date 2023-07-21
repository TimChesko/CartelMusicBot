from aiogram import Router

from src.dialogs.admin import dashboard, listening

router = Router()

router.include_routers(dashboard.router, listening.router)
