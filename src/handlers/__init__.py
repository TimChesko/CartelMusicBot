from aiogram import Router

from . import private
from ..middlewares.chat_actions import ChatActions

router = Router()
router.message.middleware(ChatActions())
router.include_router(private.router)
