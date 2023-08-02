from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaId, MediaAttachment
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Cancel, Back
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.models.track import TrackHandler
from src.models.user import UserHandler
from src.utils.fsm import ListeningNewTrack


async def set_music_file(msg: Message, _, manager: DialogManager):
    manager.dialog_data["track"] = msg.audio.file_id
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.next()


async def set_music_title(msg: Message, _, manager: DialogManager):
    manager.dialog_data["track_title"] = msg.text
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.next()


async def on_finish_getter(dialog_manager: DialogManager, **_kwargs):
    audio_id = dialog_manager.dialog_data['track']
    audio = MediaAttachment(ContentType.AUDIO, file_id=MediaId(audio_id))
    return {
        'title': dialog_manager.dialog_data['track_title'],
        'audio': audio
    }


async def nickname_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user = await UserHandler(data['session_maker'], data['database_logger']) \
        .get_user_by_tg_id(data['event_from_user'].id)
    return {
        "nickname": user.nickname,
    }


async def on_finish_new_track(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    await TrackHandler(data['session_maker'], data['database_logger']).add_new_track(
        user_id=callback.from_user.id,
        track_title=manager.dialog_data["track_title"],
        file_id_audio=manager.dialog_data["track"]
    )
    await callback.message.edit_caption(caption=f'Трек "{manager.dialog_data["track_title"]}" отправлен на модерацию')
    manager.show_mode = ShowMode.SEND
    await manager.done()


async def other_type_handler_audio(msg: Message, _, __):
    await msg.answer("Пришлите трек в формате mp3")


async def other_type_handler_text(msg: Message, _, __):
    await msg.answer("Пришлите название трека")


new_track = Dialog(
    Window(
        Format("{nickname}, скиньте ваш трек"),
        Cancel(Const("Назад")),
        MessageInput(set_music_file, content_types=[ContentType.AUDIO]),
        MessageInput(other_type_handler_audio),
        state=ListeningNewTrack.start,
        getter=nickname_getter
    ),
    Window(
        Const("Дайте название вашему треку"),
        MessageInput(set_music_title, content_types=[ContentType.TEXT]),
        MessageInput(other_type_handler_text),
        state=ListeningNewTrack.title
    ),
    Window(
        Format('Подтверждение отправки трека "{title}"'),
        DynamicMedia('audio'),
        Row(
            Button(Const("Подтверждаю"), on_click=on_finish_new_track, id="approve_track"),
            Back(Const("Изменить"), id="edit_track"),
        ),
        Cancel(Const("Вернуться в главное меню")),
        state=ListeningNewTrack.finish,
        getter=on_finish_getter
    ),
)
