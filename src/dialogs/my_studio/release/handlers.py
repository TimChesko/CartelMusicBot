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
from src.dialogs.utils.common import format_date, context_maker
from src.models.release import ReleaseHandler
from src.models.personal_data import PersonalDataHandler
from src.models.tables import PersonalData
from src.models.tracks import TrackHandler
from src.utils.enums import Status
from src.utils.fsm import ReleaseTracks, ReleasePage1, ReleasePage2, ReleasePage3


async def on_release(_, __, manager: DialogManager, release_id):
    data = manager.middleware_data
    manager.dialog_data['release_id'] = release_id
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release(release_id)
    if all([release.signed_status is None, release.unsigned_status != Status.APPROVE]):
        await manager.start(ReleasePage1.main, data={'release_id': release_id}, show_mode=ShowMode.EDIT)
    elif all([release.mail_track_status is None, release.signed_status != Status.APPROVE]):
        await manager.start(ReleasePage2.main, data={'release_id': release_id}, show_mode=ShowMode.EDIT)
    elif all([release.signed_status == Status.APPROVE, release.mail_track_status != Status.APPROVE]):
        await manager.start(ReleasePage3.main, data={'release_id': release_id}, show_mode=ShowMode.EDIT)


async def create_release(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).add_new_release(callback.from_user.id)


async def clear_release_tracks(__, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).delete_release_id_from_tracks(
        manager.start_data['release_id'])


async def attach_tracks_to_release(__, _, manager: DialogManager):
    await manager.start(state=ReleaseTracks.start, data={'release_id': manager.start_data['release_id']},
                        show_mode=ShowMode.EDIT)


async def set_release_title(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_title(manager.start_data['release_id'],
                                                                                   msg.text)
    manager.start_data['title'] = msg.text
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.back()


async def release_title_oth(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите название альбома в виде сообщения")


async def set_release_cover(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_cover(manager.start_data['release_id'],
                                                                                   msg.document.file_id)
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.switch_to(ReleasePage1.main)


# TODO переделать other type в одну функцию для всего блока
async def release_cover_oth(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите обложку альбома в виде файла")


async def all_tracks_selected(__, _, manager: DialogManager):
    data = manager.middleware_data
    widget = manager.find('release_tracklist')
    tracklist = widget.get_checked()
    await TrackHandler(data['session_maker'], data['database_logger']).update_release_id(list(map(int, tracklist)),
                                                                                         manager.start_data[
                                                                                             'release_id'])
    await manager.done()


async def to_choose_tracks(__, _, manager: DialogManager):
    await manager.start(state=ReleaseTracks.start, data={'release_id': manager.start_data['release_id']},
                        show_mode=ShowMode.EDIT)


async def on_approvement_lvl1(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    bot: Bot = data['bot']
    personal: PersonalData = await PersonalDataHandler(data['session_maker'],
                                                       data['database_logger']).get_all_personal_data(
        callback.from_user.id)
    track_list, release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_track_with_release(
        manager.start_data['release_id'])
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, 'files', 'template.docx')
    cover_path = os.path.join(current_directory, 'files', f'{release.release_cover}.jpg')
    doc = DocxTemplate(file_path)
    await bot.download(release.release_cover, cover_path)
    context = context_maker(personal, track_list, release, cover_path)
    temp_file = os.path.join(current_directory, 'files', f"{callback.from_user.id}.docx")
    doc.render(context)
    doc.save(temp_file)
    image_from_pc = FSInputFile(temp_file)
    msg = await callback.message.answer_document(image_from_pc)
    # await bot.delete_message(callback.from_user.id, msg.message_id)
    # await ReleaseHandler(data['session_maker'], data['database_logger']).update_unsigned_state(
    #     manager.start_data['release_id'], msg.document.file_id)
    os.remove(temp_file)
    os.remove(cover_path)


async def delete_release(__, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).delete_release(
        manager.start_data['release_id'])
    await manager.done()


async def release_ld_oth(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите лицензионный договор в виде файла")


async def set_release_ld(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_ld(manager.start_data['release_id'],
                                                                                msg.document.file_id)
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.switch_to(ReleasePage2.main)


async def on_approvement_lvl2(_, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).update_signed_state(
        manager.start_data['release_id'])


async def set_release_mail(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_mail_track(
        manager.start_data['release_id'],
        msg.photo[0].file_id)
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.switch_to(ReleasePage3.main)


async def release_mail_oth(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите трек номер в виде фото с сжатием")


async def on_approvement_lvl3(_, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).update_mail_state(
        manager.start_data['release_id'])
