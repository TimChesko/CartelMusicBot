from aiogram import Router

from . import private
from ..middlewares.chat_actions import ChatActions
from ..service.diologs_collector import DialogsCollector

router = Router()
router.message.middleware(ChatActions())
router.include_router(private.router)

collector = DialogsCollector()
collector.include_dialog(private.collector)
