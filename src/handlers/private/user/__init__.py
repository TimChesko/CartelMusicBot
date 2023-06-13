from aiogram import Router

from src.service.diologs_collector import DialogsCollector
from . import start

router = Router()
router.include_router(start.router)

collector = DialogsCollector()
collector.include_dialog(start.dialogs)
