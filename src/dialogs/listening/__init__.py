from aiogram import Router

from src.dialogs.listening import edit, new, menu, moderator

router = Router()

router.include_routers(menu.listening_menu, edit.edit_track, new.new_track, moderator.router)
