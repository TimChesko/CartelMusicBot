import datetime
import os

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Group, Checkbox
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, List, Multi
from docxtpl import DocxTemplate

from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_BACK
from src.dialogs.utils.common import format_date
from src.models.release import ReleaseHandler
from src.models.personal_data import PersonalDataHandler
from src.models.tables import PersonalData
from src.utils.enums import Status
from src.utils.fsm import ReleasePage, ReleaseTracks

delete = Button(Const('Удалить'), on_click=delete_release, id='delete_release', when='end')

swap_docs = Checkbox(Const("🔘 Обложка/Договор"),
                     Const("Обложка/Договор 🔘"),
                     id='swap_docs',
                     on_click=change_state,
                     default=True)

release_info = Multi(
    Format('Релиз: <b>"{title}"</b>'),
    Const('Треки в релизе:'),
    List(Format('--- "{item.track_title}"'), items='tracks'),
    Const("\n ОЖИДАЙТЕ ПРОВЕРКУ", when='wait - process'),
    Const('Ваш трек находится на стадии отгрузки, ожидайте.', when='aggregate - end'),
    sep='\n'
)

main = Dialog(
    Window(
        release_info,
        DynamicMedia('doc'),
        Group(
            SwitchTo(Format('{text_title}'), id='create_release_title', state=ReleasePage.title),
            SwitchTo(Format('{text_cover}'), id='create_release_cover', state=ReleasePage.cover),
            Button(Format('{text_tracks}'), id='add_tracks_to_release', on_click=choose_track),
            width=2,
            when='unsigned'
        ),
        Group(
            Button(Const('Очистить треки'), on_click=clear_tracks, id='clear_tracks', when='when_clear'),
            Button(Const('Отправить на проверку'), id='on_process_unsigned', on_click=on_approvement1lvl,
                   when='unsigned_when'),
            width=2,
            when='unsigned'
        ),
        delete,
        state=ReleasePage.lvl1,
        getter=lvl1_getter
    ),
    Window(
        release_info,
        swap_docs,
        SwitchTo(Format('{ld}'), 'users_ld', state=ReleasePage.ld),
        Button(Const('Отправить на проверку'), id='on_process_signed', on_click=on_approvement2lvl,
               when='signed_when'),
        delete,
        state=ReleasePage.lvl2
    ),
    Window(
        release_info,
        swap_docs,
        SwitchTo(Format('{mail_track}'), 'users_mail', state=ReleasePage.mail),
        Button(Const('Отправить на проверку'), id='on_process_mail', on_click=on_approvement3lvl, when='mail_when'),
        delete,
        state=ReleasePage.lvl3
    )
)
