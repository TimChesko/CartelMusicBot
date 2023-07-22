import logging
from datetime import datetime
from typing import Any

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram.utils.deep_linking import create_deep_link
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Back, Row, Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.tracks import TrackHandler
from src.utils.fsm import TrackApprove, StudioEdit


async def on_start(data: Any, manager: DialogManager):
    await on_start_copy_start_data(data, manager)
    manager.dialog_data['track'] = {"track_id": int(manager.dialog_data['track_id'])}


async def add_title(callback: CallbackQuery, _, manager: DialogManager):
    middleware_data = manager.middleware_data
    dialog_data = manager.dialog_data

    data_key = callback.data.split("_")[-1]
    track = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        get_track_by_id(int(dialog_data['track_id']))
    manager.dialog_data['track'].update({data_key: track.track_title})
    await manager.next()


async def add_author_text(_, __, manager: DialogManager):
    manager.dialog_data['track'].update({"words_status": True})
    await manager.next()


async def add_author_music(_, __, manager: DialogManager):
    manager.dialog_data['track'].update({"beat_status": True})
    await manager.next()


async def on_process(_, result: Any, manager: DialogManager):
    if result is not None:
        manager.dialog_data['track'].update(result)
        logging.debug(manager.dialog_data['track'])
        await manager.next()


async def save_document(msg: Message, _, manager: DialogManager):
    manager.dialog_data['track'].update({"text_file_id": msg.document.file_id})
    await manager.next()


async def is_time_format(input_string):
    try:
        datetime.strptime(input_string, '%H:%M')
        return True
    except ValueError:
        return False


async def save_time_track(msg: Message, _, manager: DialogManager, __):
    if await is_time_format(msg.text):
        manager.dialog_data['track'].update({"tiktok_time": msg.text})
        await manager.next()
    else:
        await manager.switch_to(TrackApprove.time_track)


async def save_data_callback(callback: CallbackQuery, _, manager: DialogManager):
    answer = callback.data.split("_")[-1]
    manager.dialog_data['track'].update({"explicit_lyrics": bool(answer)})
    logging.debug(manager.dialog_data['track'])
    await manager.next()


async def save_data_feat(callback: CallbackQuery, _, manager: DialogManager):
    answer = callback.data.split("_")[-1]
    manager.dialog_data['feat'] = bool(answer)
    await manager.next()


async def finish(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.dialog_data['track']
    middleware_data = manager.middleware_data
    track_id_info = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        add_track_info(data)
    if manager.dialog_data['feat']:
        link = create_deep_link("DurakTonBot",
                                link_type="start",
                                payload=f"track_feat_{track_id_info}",
                                encode=True)
        await callback.message.answer("Данные занесены в базу данных. Чтобы они отправились на модерацию, "
                                      "пригласите по данной ссылке участника фита.\n"
                                      f"Ссылка: {link}")
    else:
        await callback.message.answer("Данные отправлены на модерацию")
    manager.show_mode = ShowMode.SEND
    await manager.done()


dialog = Dialog(
    Window(
        Const("Подтвердите название трека\n{title}"),
        Start(Const("Изменить"), id="studio_edit_title", state=StudioEdit.title),
        Row(
            Cancel(Const("Назад")),
            Button(Const("Подтвердить"), id="studio_title", on_click=add_title),
        ),
        state=TrackApprove.title
    ),
    Window(
        Const("Пришлите файл с текстом трека в формате txt или docs"),
        MessageInput(
            func=save_document,
            content_types=ContentType.DOCUMENT
        ),
        Back(Const("Назад")),
        state=TrackApprove.text
    ),
    Window(
        Const("Автор текста"),
        Row(
            Start(Const("Другой человек"), id="studio_text_other", state=StudioEdit.author_text),
            Button(Const("Я и есть автор"), id="studio_text_author", on_click=add_author_text),
        ),
        Back(Const("Назад")),
        state=TrackApprove.author_text
    ),
    Window(
        Const("Автор бита"),
        Row(
            Start(Const("Другой человек"), id="studio_music_other", state=StudioEdit.author_beat),
            Button(Const("Я и есть автор"), id="studio_music_author", on_click=add_author_music),
        ),
        Back(Const("Назад")),
        state=TrackApprove.author_music
    ),
    Window(
        Const("Тип трека - фит ?"),
        Button(Const("Да"), id="track_feat_true", on_click=save_data_feat),
        Button(Const("Это не фит"), id="track_feat_false", on_click=save_data_feat),
        state=TrackApprove.feat
    ),
    Window(
        Const("Скиньте время трека\nПример: 1:23"),
        TextInput(
            id="track_time",
            on_success=save_time_track,
        ),
        state=TrackApprove.time_track
    ),
    Window(
        Const("Наличие нецензурной лексики"),
        Button(Const("Не имеется"), id="track_profanity_false", on_click=save_data_callback),
        Button(Const("Имеется"), id="track_profanity_true", on_click=save_data_callback),
        state=TrackApprove.profanity
    ),
    Window(
        Const("Отправить на модерацию ?"),
        Button(Const("Да"), id="track_finish_true", on_click=finish),
        Back(Const("Назад")),
        state=TrackApprove.finish
    ),
    on_process_result=on_process,
    on_start=on_start
)
