from datetime import datetime
from typing import Any

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram.utils.deep_linking import create_deep_link
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Start
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_BACK, BTN_CANCEL_BACK, TXT_CONFIRM, TXT_EDIT, TXT_FALSE, TXT_TRUE
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.track_info import TrackInfoHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import TrackApprove, StudioEdit


async def on_start(data: Any, manager: DialogManager):
    await on_start_copy_start_data(data, manager)
    manager.dialog_data['track'] = {}


async def add_title(callback: CallbackQuery, _, manager: DialogManager):
    middleware_data = manager.middleware_data
    track_id = manager.dialog_data['track_id']
    track = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']).get_track_by_id(
        int(track_id))
    manager.dialog_data['track'].update({callback.data.split("_")[-1]: track.track_title})
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
        await manager.next()


async def save_document(msg: Message, _, manager: DialogManager):
    await msg.delete()
    manager.dialog_data['track'].update({"text_file_id": msg.document.file_id})
    await manager.next()


async def is_time_format(input_string):
    try:
        datetime.strptime(input_string, '%H:%M')
        return True
    except ValueError:
        return False


async def save_time_track(msg: Message, _, manager: DialogManager, __):
    await msg.delete()
    if await is_time_format(msg.text):
        manager.dialog_data['track'].update({"tiktok_time": msg.text})
        await manager.next()
    else:
        await manager.switch_to(TrackApprove.time_track)


async def save_data_callback(callback: CallbackQuery, _, manager: DialogManager):
    answer = callback.data.split("_")[-1]
    manager.dialog_data['track'].update({"explicit_lyrics": bool(answer)})
    await manager.next()


async def save_data_feat(_, __, manager: DialogManager):
    manager.dialog_data['track'].update({'feat_status': False})
    await manager.next()


async def finish(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.dialog_data.get('track')
    middleware_data = manager.middleware_data
    if data['feat_status']:
        data.update({"status": "wait_feat"})
    else:
        data.update({"status": "process"})
    await TrackInfoHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        add_track_info(int(manager.dialog_data['track_id']), data)
    if data['feat_status']:
        bot: Bot = manager.middleware_data['bot']
        bot_info = await bot.me()
        link = create_deep_link(bot_info.username,
                                link_type="start",
                                payload=f"track_feat_{manager.dialog_data['track_id']}",
                                encode=True)
        await callback.message.answer("Данные занесены в базу данных. Чтобы они отправились на модерацию, "
                                      "пригласите по данной ссылке участника фита.\n"
                                      f"Ссылка: {link}", disable_web_page_preview=True)
    else:
        await callback.message.answer("Данные отправлены на модерацию")
    manager.show_mode = ShowMode.SEND
    await manager.done()


async def get_title(dialog_manager: DialogManager, **_kwargs):
    middleware_data = dialog_manager.middleware_data
    track_id = dialog_manager.dialog_data['track_id']
    track = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        get_track_by_id(int(track_id))
    return {"title": track.track_title}


dialog = Dialog(
    Window(
        Const("Подтвердите название трека:"),
        Format("<b>{title}</b>"),
        Start(TXT_EDIT, id="studio_edit_title", state=StudioEdit.title),
        Row(
            BTN_CANCEL_BACK,
            Button(TXT_CONFIRM, id="studio_title", on_click=add_title),
        ),
        getter=get_title,
        state=TrackApprove.title
    ),
    Window(
        Const("Пришлите файл с текстом трека в формате txt или docs"),
        MessageInput(
            func=save_document,
            content_types=ContentType.DOCUMENT
        ),
        BTN_BACK,
        state=TrackApprove.text
    ),
    Window(
        Const("Кто автор текста ?"),
        Row(
            Start(Const("Другой человек"), id="studio_text_other", state=StudioEdit.author_text),
            Button(Const("Я и есть автор"), id="studio_text_author", on_click=add_author_text),
        ),
        BTN_BACK,
        state=TrackApprove.author_text
    ),
    Window(
        Const("Кто автор бита ?"),
        Row(
            Start(Const("Другой человек"), id="studio_music_other", state=StudioEdit.author_beat),
            Button(Const("Я и есть автор"), id="studio_music_author", on_click=add_author_music),
        ),
        BTN_BACK,
        state=TrackApprove.author_music
    ),
    Window(
        Const("Это фит ?"),
        Row(
            Start(TXT_TRUE, id="track_feat_true", state=StudioEdit.feat_percent),
            Button(TXT_FALSE, id="track_feat_false", on_click=save_data_feat),
        ),
        BTN_BACK,
        state=TrackApprove.feat
    ),
    Window(
        Const("Пришлите время трека\nПример: 1:23"),
        TextInput(
            id="track_time",
            on_success=save_time_track,
        ),
        BTN_BACK,
        state=TrackApprove.time_track
    ),
    Window(
        Const("В треке присутствует нецензурная лексика ?"),
        Row(
            Button(TXT_FALSE, id="track_profanity_false", on_click=save_data_callback),
            Button(TXT_TRUE, id="track_profanity_true", on_click=save_data_callback),
        ),
        BTN_BACK,
        state=TrackApprove.profanity
    ),
    Window(
        Const("Отправить на модерацию ?"),
        Row(
            BTN_BACK,
            Button(TXT_TRUE, id="track_finish_true", on_click=finish),
        ),
        state=TrackApprove.finish
    ),
    on_process_result=on_process,
    on_start=on_start
)
