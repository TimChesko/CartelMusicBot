from aiogram import Router

from src.middlewares.check_privilege import CheckPrivilege
from . import common, moderator

router = Router()

router.message.middleware(
    CheckPrivilege("moderator")
)

router.include_routers(common.router,
                       moderator.router)
