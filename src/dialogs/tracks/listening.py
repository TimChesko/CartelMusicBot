from operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Cancel, Back, Start, ScrollingGroup, Multiselect
from aiogram_dialog.widgets.text import Format, Const

from src.data import config
from src.models.chats import ChatsHandler
from src.models.user import UserHandler
from src.utils.fsm import Listening, ListeningNewTrack, ListeningEditTrack


async def get_music_file(message: Message, _, manager: DialogManager):
    if manager.is_preview():
        await manager.next()
        return
    manager.dialog_data["track"] = message.audio.file_id
    await manager.next()


async def other_type_handler_audio(message: Message, _, __):
    await message.answer("Пришлите трек в формате mp3")


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.middleware_data
    user_nickname = await UserHandler(data['engine'], data['database_logger']) \
        .get_user_nickname(data['event_from_user'].id)
    return {
        "nickname": user_nickname,
    }


dialog = Dialog(
    Window(
        Const("Выберете действие:"),
        Start(Const("Измненный трек"), id="edit_old_track", state=ListeningEditTrack.select_track),
        Start(Const("Новый трек"),
              id="add_new_track",
              state=ListeningNewTrack.track),
        Cancel(Const("Назад")),
        state=Listening.start
    )
)


async def tracks_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    tracks = await ChatsHandler(data['engine'], data['database_logger']).has_reject_by_tg_id(data['event_from_user'].id,
                                                                                             1)
    return {
        "tracks": [(f"Track: {i.track_title}", i.id) for i in tracks[0]],
    }


edit_old_track = Dialog(
    Window(
        Const("Выберете трек"),
        ScrollingGroup(
            Multiselect(
                Format("✓ {item[0]}"),
                Format("{item[0]}"),
                id="ms",
                items="tracks",
                item_id_getter=itemgetter(1),
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Back(),
        getter=tracks_getter,
        state=ListeningEditTrack.select_track,
    )
)


async def on_finish_add(callback: CallbackQuery, _, dialog_manager: DialogManager):
    data = dialog_manager.middleware_data
    chat_id = config.CHATS_BACKUP[0]  # TODO нужный чат
    user = await UserHandler(data['engine'], data['database_logger']).get_all_by_tg_id(callback.from_user.id)
    user_name = user.tg_id if user.tg_username is None else f"@{user.tg_username}"
    msg_audio = await data['bot'].send_document(chat_id, document=dialog_manager.dialog_data["track_text"], )
    msg_audio_text = await data['bot'].send_audio(chat_id, audio=dialog_manager.dialog_data["track"],
                                                  reply_to_message_id=msg_audio.message_id,
                                                  caption=f"Title: {dialog_manager.dialog_data['track_title']}\n" \
                                                          f"User: {user_name} / nickname: {user.nickname}")
    await ChatsHandler(data['engine'], data['database_logger']).add_track_to_chat(
        chat_id, callback.from_user.id,
        dialog_manager.dialog_data["track_title"],
        msg_audio.message_id, msg_audio_text.message_id,
        dialog_manager.dialog_data["track"], dialog_manager.dialog_data["track_text"]
    )
    await callback.message.answer("Ваш трек отправлен на модерацию")
    dialog_manager.show_mode = ShowMode.SEND
    if dialog_manager.is_preview():
        await dialog_manager.done()
        return
    await dialog_manager.done()


async def other_type_handler_docs(message: Message, _, __):
    await message.answer("Пришлите текст трека в формате docs или txt")


async def other_type_handler_text(message: Message, _, __):
    await message.answer("Пришлите название трека")


async def get_document_file(message: Message, _, manager: DialogManager):
    if manager.is_preview():
        await manager.next()
        return
    manager.dialog_data["track_text"] = message.document.file_id
    await manager.next()


async def get_music_title(message: Message, _, manager: DialogManager):
    if manager.is_preview():
        await manager.next()
        return
    manager.dialog_data["track_title"] = message.text
    await manager.next()


new_track = Dialog(
    Window(
        Format("{nickname}, скиньте ваш трек"),
        Cancel(Const("Назад")),
        MessageInput(get_music_file, content_types=[ContentType.AUDIO]),
        MessageInput(other_type_handler_audio),
        state=ListeningNewTrack.track
    ),
    Window(
        Const("Скиньте документ в формате txt или docs с текстом трека"),
        MessageInput(get_document_file, content_types=[ContentType.DOCUMENT]),
        MessageInput(other_type_handler_docs),
        state=ListeningNewTrack.text
    ),
    Window(
        Const("Дайте название вашему треку"),
        MessageInput(get_music_title, content_types=[ContentType.TEXT]),
        MessageInput(other_type_handler_text),
        state=ListeningNewTrack.title
    ),
    Window(
        Const("Подтверждение отправки данного трека c текстом:"),
        Row(
            Button(Const("Подтверждаю"), on_click=on_finish_add, id="approve_track"),
            Back(Const("Изменить"), id="edit_track"),
        ),
        Cancel(Const("Вернуться в главное меню")),
        state=ListeningNewTrack.apply
    ),
    getter=get_data
)
