import logging
from operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Cancel, Back, ScrollingGroup, Select
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.data import config
from src.dialogs.listening.menu import tracks_getter
from src.dialogs.listening.new import other_type_handler_audio
from src.keyboards.inline.listening import markup_edit_listening
from src.models.tracks import TrackHandler
from src.models.user import UserHandler
from src.utils.fsm import ListeningEditTrack


async def on_item_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item: str):
    manager.dialog_data["track_id"] = int(selected_item)
    logging.info(selected_item)
    await manager.next()


async def on_finish_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    track_id = dialog_manager.dialog_data['track_id']
    title, file_id_audio = await TrackHandler(data['session_maker'], data['database_logger']).get_title_and_file_id_by_id(
        track_id)
    audio = MediaAttachment(ContentType.AUDIO, file_id=MediaId(file_id_audio))
    dialog_manager.dialog_data['track_title'] = title
    return {
        'title': title,
        'audio': audio
    }


async def set_music_file_for_edit(msg: Message, _, manager: DialogManager):
    manager.dialog_data["track"] = msg.audio.file_id
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.next()


async def on_finish_old_track(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    track_id = manager.dialog_data['track_id']
    chat_id = config.CHATS_BACKUP[0]  # TODO нужный чат
    nickname, tg_username = await UserHandler(data['session_maker'], data['database_logger']).get_nicknames_by_tg_id(
        callback.from_user.id)
    user_name = callback.from_user.id if tg_username is None else f"@{callback.from_user.username}"
    await TrackHandler(data['session_maker'], data['database_logger']).update_track_file_id_audio(
        track_id=track_id,
        file_id_audio=manager.dialog_data["track"]
    )
    await TrackHandler(data['session_maker'], data['database_logger']).set_new_status_track(track_id, 'process')
    msg_audio: Message = await data['bot'].send_audio(chat_id=chat_id,
                                                      audio=manager.dialog_data["track"],
                                                      caption=f"ПОВТОРНОЕ ПРОСЛУШИВАНИЕ \n"
                                                              f"Серийный номер: #{track_id}"
                                                              f"Title: {manager.dialog_data['track_title']}\n"
                                                              f"User: {user_name} / nickname: {nickname}",
                                                      reply_markup=markup_edit_listening(track_id))
    await TrackHandler(data['session_maker'], data['database_logger']).set_task_msg_id_to_tracks(track_id,
                                                                                          msg_audio.message_id)
    await callback.message.edit_caption(
        caption=f'Трек "{manager.dialog_data["track_title"]}" повторно отправлен на модерацию')
    manager.show_mode = ShowMode.SEND
    await manager.done()


edit_track = Dialog(
    Window(
        Const("Выберите трек"),
        ScrollingGroup(
            Select(
                Format("🔴 {item[0]}"),
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
    ),
    Window(
        Format("Скиньте новый файл трека {title}"),
        Cancel(Const("Назад")),
        MessageInput(set_music_file_for_edit, content_types=[ContentType.AUDIO]),
        MessageInput(other_type_handler_audio),
        state=ListeningEditTrack.select_track,
        getter=on_finish_getter
    ),
    Window(
        Format('Подтверждение отправки трека "{title}"'),
        DynamicMedia('audio'),
        Row(
            Button(Const("Подтверждаю"), on_click=on_finish_old_track, id="approve_old_track"),
            Back(Const("Изменить"), id="edit_old_track"),
        ),
        Cancel(Const("Вернуться в главное меню")),
        state=ListeningEditTrack.finish,
        getter=on_finish_getter
    ),
)
