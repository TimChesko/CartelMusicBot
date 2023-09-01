from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager


async def on_release(_, __, manager: DialogManager, data):
    manager.dialog_data['release_id'] = data
    await manager.next()


async def on_track(callback: CallbackQuery, _, manager: DialogManager):
    pass
