import logging
from operator import itemgetter
from typing import Any

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Cancel, Back, Start, ScrollingGroup, Multiselect, SwitchTo, Select
from aiogram_dialog.widgets.text import Format, Const

from src.data import config
from src.keyboards.inline.listening import markup_listening
from src.models.tracks import TrackHandler
from src.models.user import UserHandler
from src.utils.fsm import Listening, ListeningNewTrack, ListeningEditTrack


async def get_music_file(message: Message, _, manager: DialogManager):
    if manager.is_preview():
        await manager.next()
        return
    manager.dialog_data["track"] = message.audio.file_id
    await manager.next()


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.middleware_data
    user_nickname = await UserHandler(data['engine'], data['database_logger']) \
        .get_user_nickname_by_tg_id(data['event_from_user'].id)
    return {
        "nickname": user_nickname,
    }


async def tracks_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    rejects = await TrackHandler(data['engine'], data['database_logger']).has_reject_by_tg_id(
        data['event_from_user'].id)
    reject_tracks = await TrackHandler(data['engine'], data['database_logger']).get_rejected_by_tg_id(
        data['event_from_user'].id)
    logging.info(rejects)
    logging.info(reject_tracks)
    return {
        "rejects_check": rejects,
        'reject_tracks': reject_tracks
    }


async def on_finish_add(callback: CallbackQuery, _, dialog_manager: DialogManager):
    data = dialog_manager.middleware_data
    chat_id = config.CHATS_BACKUP[0]  # TODO нужный чат
    nickname, tg_username = await UserHandler(data['engine'], data['database_logger']).get_all_by_tg_id(
        callback.from_user.id)
    user_name = callback.from_user.id if tg_username is None else f"@{callback.from_user.username}"
    await TrackHandler(data['engine'], data['database_logger']).add_track_to_tracks(
        user_id=callback.from_user.id,
        track_title=dialog_manager.dialog_data["track_title"],
        file_id_audio=dialog_manager.dialog_data["track"]
    )
    track_id = await TrackHandler(data['engine'], data['database_logger']).get_id_by_file_id_audio(
        dialog_manager.dialog_data["track"])
    msg_audio: Message = await data['bot'].send_audio(chat_id=chat_id,
                                                      audio=dialog_manager.dialog_data["track"],
                                                      caption=f"Title: {dialog_manager.dialog_data['track_title']}\n" \
                                                              f"User: {user_name} / nickname: {nickname}",
                                                      reply_markup=markup_listening(track_id))
    await TrackHandler(data['engine'], data['database_logger']).set_task_msg_id_to_tracks(track_id,
                                                                                          msg_audio.message_id)
    await callback.message.answer("Ваш трек отправлен на модерацию")
    dialog_manager.show_mode = ShowMode.SEND
    if dialog_manager.is_preview():
        await dialog_manager.done()
        return
    await dialog_manager.done()


async def other_type_handler_audio(message: Message, _, __):
    await message.answer("Пришлите трек в формате mp3")


async def other_type_handler_text(message: Message, _, __):
    await message.answer("Пришлите название трека")


async def get_music_title(message: Message, _, manager: DialogManager):
    if manager.is_preview():
        await manager.next()
        return
    manager.dialog_data["track_title"] = message.text
    await manager.next()


track_menu = Dialog(
    Window(
        Const('Удиви или скинь переделанное'),
        Start(Const('Удивляю'), state=ListeningNewTrack.start, id='listening_new_track'),
        Start(Const('Переделал'), state=ListeningEditTrack.start, id='listening_old_track', when='rejects_check'),
        Cancel(Const('Назад')),
        state=Listening.start,
        getter=tracks_getter
    )
)

new_track = Dialog(
    Window(
        Format("{nickname}, скиньте ваш трек"),
        Cancel(Const("Назад")),
        MessageInput(get_music_file, content_types=[ContentType.AUDIO]),
        MessageInput(other_type_handler_audio),
        state=ListeningNewTrack.start
    ),
    Window(
        Const("Дайте название вашему треку"),
        MessageInput(get_music_title, content_types=[ContentType.TEXT]),
        MessageInput(other_type_handler_text),
        state=ListeningNewTrack.title
    ),
    Window(
        Const("Подтверждение отправки данного трека"),
        Row(
            Button(Const("Подтверждаю"), on_click=on_finish_add, id="approve_track"),
            Back(Const("Изменить"), id="edit_track"),
        ),
        Cancel(Const("Вернуться в главное меню")),
        state=ListeningNewTrack.finish
    ),
    getter=get_data
)


async def on_item_selected(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        selected_item: str):
    await callback.answer(selected_item)


# async def track_id_getter(track_title) -> str:
#     data = dialog_manager.middleware_data
#     await TrackHandler()


old_track = Dialog(
    Window(
        Const("Выберите трек"),
        ScrollingGroup(
            Select(
                Format("🔴{item}"),
                id="ms",
                items="reject_tracks",
                item_id_getter=itemgetter(1),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Cancel(),
        getter=tracks_getter,
        state=ListeningEditTrack.start,
    )
)
