from aiogram_dialog import DialogManager


async def on_start_copy_start_data(_, dialog_manager: DialogManager):
    if dialog_manager.current_context().start_data:
        dialog_manager.dialog_data.update(
            dialog_manager.current_context().start_data
        )
