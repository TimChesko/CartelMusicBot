from aiogram import Router

from src.middlewares.check_privilege import CheckPrivilege
from . import common

router = Router()

router.message.middleware(
    CheckPrivilege("moderator")
)

router.include_router(common.router)
