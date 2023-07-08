from aiogram import Router

from . import private, group
from ..middlewares.chat_actions import ChatActions

router = Router()
router.message.middleware(ChatActions())
router.include_router(private.router)
router.include_router(group.router)
