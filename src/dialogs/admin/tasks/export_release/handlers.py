from aiogram_dialog import DialogManager


async def on_release(_, __, manager: DialogManager, data):
    manager.dialog_data['release_id'] = data
    await manager.next()


async def on_track(_, __, manager: DialogManager, data):
    manager.dialog_data['track_id'] = data
    await manager.next()
