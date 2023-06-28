import logging

from aiogram_dialog import DialogManager, StartMode, ShowMode

from src.utils.fsm import StartMenu


async def on_start_copy_start_data(_, dialog_manager: DialogManager):
    if dialog_manager.current_context().start_data:
        dialog_manager.dialog_data.update(
            dialog_manager.current_context().start_data
        )


async def on_unknown_intent(event, dialog_manager: DialogManager):
    """Example of handling UnknownIntent Error and starting new dialog."""
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        StartMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,
    )


async def on_unknown_state(event, dialog_manager: DialogManager):
    """Example of handling UnknownState Error and starting new dialog."""
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        StartMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,
    )
