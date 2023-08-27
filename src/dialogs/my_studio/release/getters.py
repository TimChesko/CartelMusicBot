import datetime
import logging
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
from src.models.tables import PersonalData, Track, Release
from src.models.tracks import TrackHandler
from src.utils.enums import Status
from src.utils.fsm import ReleaseTracks


async def getter(dialog_manager: DialogManager, **_kwargs):
    release, tracks = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release_scalar(
        dialog_manager.start_data['release_id'])
    is_cover = None
    if release.release_cover:
        doc_id = release.release_cover if dialog_manager.dialog_data['doc_state'] is True else release.unsigned_license
        is_cover = MediaAttachment(ContentType.DOCUMENT, file_id=MediaId(doc_id))
    return {
        'unsigned': not release.unsigned_state or release.unsigned_state == 'reject',
        'signed': release.unsigned_state == 'approve' and not release.signed_state or release.signed_state == 'reject',
        'signed_when': release.signed_license is not None,
        'mail': release.signed_state == 'approve' and not release.mail_track_state or release.mail_track_state == 'reject',
        'mail_when': release.mail_track_photo is not None,
        'end': release.mail_track_status != 'approve'

    }


async def cover_getter(dialog_manager: DialogManager, **_kwargs):
    text = ''
    if 'error_cover' in dialog_manager.dialog_data:
        text += dialog_manager.dialog_data['error_cover']
    text += "\nПрикрепите новую обложку в виде фото без сжатия\n" \
            "Обратите внимание, обложка должна быть в соотношении 1:1"
    return {
        'window_text': text
    }


async def create_new_release_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release_by_user_id(
        dialog_manager.event.from_user.id)
    return {
        'releases': [(release_id, title if title else 'Новый альбом') for release_id, title in release]
    }


def release_info(tracks: Track, release: Release):
    return {
        'title': release.release_title if release.release_title else f'Новый альбом №{release.id}',
        'tracks': tracks,
        'on_process': release.unsigned_status == Status.PROCESS or release.signed_status == Status.PROCESS or release.mail_track_status == Status.PROCESS,
        'on_aggregate': release.mail_track_status == Status.APPROVE,

    }


async def lvl1_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release, tracks = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release_scalar(
        dialog_manager.start_data['release_id'])
    return {
        'text_title': '✓ Название' if release.release_title else 'Дать название',
        'text_cover': '✓ Обложка' if release.release_cover else 'Прикрепить обложку',
        'text_tracks': '✓ Треки' if tracks else 'Прикрепить треки',
        'cover': MediaAttachment(ContentType.DOCUMENT,
                                 file_id=MediaId(release.release_cover)) if release.release_cover else None,
        'all_done': all((release.release_title, release.release_cover, tracks)),
        'is_process': False if release.unsigned_status == Status.PROCESS else True,
        **release_info(tracks, release)
    }


async def lvl2_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release, tracks = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release_scalar(
        dialog_manager.start_data['release_id'])
    return {
        'ld': '✓ Лиц. Договор' if release.signed_license else 'Лиц. Договор',
        'all_done': release.signed_license is not None,
        'ld_file': MediaAttachment(ContentType.DOCUMENT,
                                   file_id=MediaId(release.unsigned_license)) if release.unsigned_status else None,
        'is_process': False if release.signed_status == Status.PROCESS else True,
        **release_info(tracks, release)
    }


async def choose_tracks_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    tracks = await TrackHandler(data['session_maker'], data['database_logger']).get_for_release_multiselect(
        dialog_manager.event.from_user.id)
    return {
        'items': tracks
    }


async def lvl3_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release, tracks = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release_scalar(
        dialog_manager.start_data['release_id'])
    return {
        'mail': '✓ Трек номер' if release.mail_track_photo else 'Трек номер',
        'all_done': release.mail_track_photo is not None,
        'mail_photo': MediaAttachment(ContentType.PHOTO,
                                      file_id=MediaId(release.mail_track_photo)) if release.mail_track_photo else None,
        'is_process': False if release.mail_track_status == Status.PROCESS else True,
        **release_info(tracks, release)
    }
