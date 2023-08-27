from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaId, MediaAttachment
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Back
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.utils.buttons import BTN_CANCEL_BACK, BTN_BACK, TXT_APPROVE, TXT_EDIT
from src.models.tracks import TrackHandler
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
    support = data['config'].constant.support
    answer = await TrackHandler(data['session_maker'], data['database_logger']).add_new_track(
        user_id=callback.from_user.id,
        track_title=manager.dialog_data["track_title"],
        file_id_audio=manager.dialog_data["track"]
    )
    if answer:
        text = f'✅ Трек <b>{manager.dialog_data["track_title"]}</b> отправлен на модерацию'
    else:
        text = f'❌ Произошел сбой на стороне сервера. Обратитесь в поддержку {support}'
    await callback.message.edit_caption(caption=text)
    manager.show_mode = ShowMode.SEND
    await callback.answer(text=text, show_alert=True)
    await manager.done()


async def other_type_handler_audio(msg: Message, _, __):
    await msg.answer("🎶 Пришлите трек в формате файла - <b>.mp3</b>")


async def other_type_handler_text(msg: Message, _, __):
    await msg.answer("📝 Название трека в формате - текст\nПример: <b>Best of the best track</b>")


new_track = Dialog(
    Window(
        Format("1️⃣ {nickname}, скиньте ваш трек"),
        BTN_CANCEL_BACK,
        MessageInput(set_music_file, content_types=[ContentType.AUDIO]),
        MessageInput(other_type_handler_audio),
        state=ListeningNewTrack.start,
        getter=nickname_getter
    ),
    Window(
        Const("2️⃣ Дайте название вашему треку"),
        MessageInput(set_music_title, content_types=[ContentType.TEXT]),
        MessageInput(other_type_handler_text),
        BTN_BACK,
        state=ListeningNewTrack.title
    ),
    Window(
        Const("Подтверждение отправки трека"),
        Format("Название: <b>{title}</b>"),
        DynamicMedia('audio'),
        Row(
            Button(TXT_APPROVE, on_click=on_finish_new_track, id="approve_track"),
            Back(TXT_EDIT, id="edit_track"),
        ),
        BTN_CANCEL_BACK,
        state=ListeningNewTrack.finish,
        getter=on_finish_getter
    )
)
