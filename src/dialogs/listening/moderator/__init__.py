from aiogram import Router

from src.dialogs.listening.moderator import answer

router = Router()

router.include_router(answer.custom_answer)
