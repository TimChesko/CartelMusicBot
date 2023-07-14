import logging
from _operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput
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


async def get_text_file(message: Message, _, manager: DialogManager):
    manager.dialog_data["track_text"] = message.document.file_id
    await manager.next()


async def get_alienation_file(message: Message, _, manager: DialogManager):
    # Отчуждение
    manager.dialog_data["track_text"] = message.document.file_id
    await manager.switch_to(MyTracksApproved.set_text_author)


async def other_type_handler_docs(message: Message, _, __):
    await message.answer("Нужно прислать файл с требуемыми данными")


async def other_type_handler_text(message: Message, _, __):
    await message.answer("Пришлите название трека")


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    manager.dialog_data["track_id"] = int(selected_item)
    logging.info(selected_item)
    await manager.next()


async def set_music_title(message: Message, _, manager: DialogManager):
    manager.dialog_data["track_title"] = message.text
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
               "Актуальное название: '{track_title}'"),
        Next(Const('Обновить заголовок')),
        SwitchTo(Const('Продолжить'),
                 state=MyTracksApproved.get_text,
                 id='approved_to_get_text'),
        Cancel(),
        state=MyTracksApproved.confirm_title,
        getter=title_getter
    ),
    Window(
        Const("Дайте название вашему треку"),
        MessageInput(set_music_title,
                     content_types=[ContentType.TEXT]),
        MessageInput(other_type_handler_text),
        Cancel(),
        state=MyTracksApproved.update_title
    ),
    Window(
        Const("Скиньте документ в формате txt или docs с текстом трека"),
        MessageInput(get_text_file,
                     content_types=[ContentType.DOCUMENT]),
        MessageInput(other_type_handler_docs),
        Cancel(),
        state=MyTracksApproved.get_text
    ),
    Window(
        Const('Выберите кто является автором музыки, если бит выкуплен - понадобится отчуждение'),
        Next(Const('Выкуплен')),
        SwitchTo(Const('Процент'),
                 state=MyTracksApproved.percent_beat,
                 id='beat_percent'),
        SwitchTo(Const('Я автор'),
                 state=MyTracksApproved.set_text_author,
                 id='to_text_author'),
        Cancel(),
        state=MyTracksApproved.set_beat_author
    ),
    Window(
        Const('Пришлите отчуждение в формате PDF'),
        MessageInput(get_alienation_file,
                     content_types=[ContentType.DOCUMENT]),
        MessageInput(other_type_handler_docs),
        Cancel(),
        state=MyTracksApproved.purchased_beat
    ),
    Window(
        Const('Укажите процент битмейкера:'),
        TextInput()
    )
)
