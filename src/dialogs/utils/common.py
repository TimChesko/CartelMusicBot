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


def context_maker(personal: PersonalData, track_info: list[TrackInfo], release: Release, path, doc,
                  nickname: User.nickname):
    fullname = f'{personal.surname} {personal.first_name} {personal.middle_name}'

    context = {
        'licensor_name': f'{personal.surname} {personal.first_name[0]}.{personal.middle_name[0]}.',
        'name': fullname,
        'nickname': nickname,
        'inn_code': f'{personal.tin_self}',
        'passport': f'{personal.passport_series} {personal.passport_number}',
        'who_issued_it': f'{personal.who_issued_it}',
        'unit_code': f'{personal.unit_code}',
        'registration_address': f'{personal.registration_address}',
        'date_of_issue': f'{personal.date_of_issue}',
        'recipient': f'{personal.recipient}',
        'account_code': f'{personal.account_code}',
        'bank_recipient': f'{personal.bank_recipient}',
        'bik_code': f'{personal.bik_code}',
        'correct_code': f'{personal.correct_code}',
        'bank_inn_code': f'{personal.tin_bank}',
        'kpp_code': f'{personal.kpp_code}',
        'email': f'{personal.email}',
        'release_title': f'{release.release_title}',
        'ld_number': f'{datetime.now().strftime("%d%m%Y%")}-{release.id}',
        'date': f'{format_date()}',
        'year': datetime.now().strftime('%Y'),
        'cover': InlineImage(doc, path, width=Mm(100), height=Mm(100))
    }
    for number, track in enumerate(track_info):
        context[f'track_title{number}'] = track.title
        context[f'beat_author{number}'] = track.beatmaker_fullname if track.beatmaker_fullname else fullname
        context[f'words_author{number}'] = track.words_author_fullname if track.words_author_fullname else fullname
        context[f'min{number}'] = track.tiktok_time.split(':')[0]
        context[f'sec{number}'] = track.tiktok_time.split(':')[1]
        context[f'feat_percent{number}'] = track.feat_percent if track.feat_percent else '100'
    return context
