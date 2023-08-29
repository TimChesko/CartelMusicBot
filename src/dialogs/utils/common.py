import logging
from datetime import datetime

from aiogram_dialog import DialogManager, StartMode, ShowMode
from docx.shared import Mm
from docxtpl import InlineImage

from src.models.tables import PersonalData, Track, TrackInfo, Release, User
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


def format_date(dt: datetime = None) -> str:
    if dt is None:
        dt = datetime.now()

    months_russian = {
        1: 'января',
        2: 'февраля',
        3: 'марта',
        4: 'апреля',
        5: 'мая',
        6: 'июня',
        7: 'июля',
        8: 'августа',
        9: 'сентября',
        10: 'октября',
        11: 'ноября',
        12: 'декабря'
    }

    day = dt.day
    month = months_russian[dt.month]
    year = dt.year

    return f'«{day}» {month} {year} г.'
