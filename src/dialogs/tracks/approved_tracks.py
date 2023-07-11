import logging
from _operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Next, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.models.tracks import TrackHandler
from src.utils.fsm import MyTracksApproved


async def tracks_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    approved = await TrackHandler(data['engine'], data['database_logger']).get_approved_by_tg_id(
        data['event_from_user'].id)
    return {
        'approved_tracks': approved
    }


async def title_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    title = await TrackHandler(data['engine'], data['database_logger']).get_title_by_track_id(
        dialog_manager.dialog_data['track_id'])
    return {
        'track_title': title
    }


async def get_document_file(message: Message, _, manager: DialogManager):
    manager.dialog_data["track_text"] = message.document.file_id
    await manager.next()


async def other_type_handler_docs(message: Message, _, __):
    await message.answer("Пришлите текст трека в формате docs или txt")


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    manager.dialog_data["track_id"] = int(selected_item)
    logging.info(selected_item)
    await manager.next()


approved_filling_data = Dialog(
    Window(
        Const("Выберите трек"),
        ScrollingGroup(
            Select(
                Format("🟢 {item[0]}"),
                id="approved_tracks_item",
                items="approved_tracks",
                item_id_getter=itemgetter(1),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Cancel(),
        getter=tracks_getter,
        state=MyTracksApproved.start,
    ),
    Window(
        Const('*Инфа по треку*'),
        Next(Const('Заполнить инфу')),
        Cancel(Const('Назад')),
        state=MyTracksApproved.track_info
    ),
    Window(
        Const(
            "Вот тебе ебанутый список информации, которая тебе понадобится,"
            " чтобы прикрепить ее к треку, подготовься еб твою мать"),
        Next(Const('Продолжить')),
        Cancel(Const('Назад')),
        state=MyTracksApproved.filling_data
    ),
    Window(
        Format("Подтвердите название трека\n"
               "Актуальное название: {title}"),
        Next(Const('Обновить заголовок')),
        SwitchTo(Const('Продолжить'), state=MyTracksApproved.get_text, id='approved_to_get_text'),
        state=MyTracksApproved.confirm_title
    ),
    Window(
        Const("Скиньте документ в формате txt или docs с текстом трека"),
        MessageInput(get_document_file, content_types=[ContentType.DOCUMENT]),
        MessageInput(other_type_handler_docs),
        state=MyTracksApproved.get_text
    ),
)
