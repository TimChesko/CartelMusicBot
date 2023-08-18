from aiogram import Router

from src.dialogs.admin import dashboard, menu, registration, tasks
from src.dialogs.admin.tasks import release, listening

router = Router()

router.include_routers(menu.menu,
                       registration.reg_fullname,
                       dashboard.router,
                       tasks.router,
                       )
