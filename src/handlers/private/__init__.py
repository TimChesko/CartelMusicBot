from aiogram import Router, F
from . import user
from ...service.diologs_collector import DialogsCollector

router = Router()
router.message.filter(F.chat.type == "private")
router.include_router(user.router)

collector = DialogsCollector()
collector.include_dialog(user.collector)
