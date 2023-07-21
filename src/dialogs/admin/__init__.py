from aiogram import Router

from src.dialogs.admin import dashboard, menu, registration, listening, documents

router = Router()

router.include_routers(dashboard.router, menu.menu, registration.reg_fullname, listening.router)
router.include_router(documents.router)
