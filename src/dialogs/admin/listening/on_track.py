from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import SwitchTo, Back, Next, Button
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.models.listening_templates import ListeningTemplatesHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import AdminListening


async def cancel_task(_, __, manager: DialogManager):
    data = manager.middleware_data
    track_id = manager.dialog_data['getter_info']['track_id']
    await TrackHandler(data['session_maker'], data['database_logger']).update_checker(track_id, None)


async def approve(callback: CallbackQuery, btn: Button, manager: DialogManager):
    data = manager.middleware_data
    bot: Bot = manager.middleware_data['bot']
    track_id = manager.dialog_data['getter_info']['track_id']
    user_id = await TrackHandler(data['session_maker'], data['database_logger']).update_approve(track_id,
                                                                                                callback.from_user.id)
    text = await ListeningTemplatesHandler(data['session_maker'], data['database_logger']).get_approve_reason(
        btn.widget_id)
    await bot.send_message(chat_id=user_id, text=text)


async def info_getter(dialog_manager: DialogManager, **_kwargs):
    audio = MediaAttachment(ContentType.AUDIO, file_id=MediaId(dialog_manager.dialog_data['file']))
    return {
        **dialog_manager.dialog_data['getter_info'],
        'audio': audio
    }


info_window = Window(
    Format('Уникальный номер: {track_id}'),
    Format('Название: {title}'),
    Format('Артист: {nickname} | {username}'),
    DynamicMedia('audio'),
    Back(Const('Одобрить'),
         on_click=approve,
         id='approve'),
    Back(Const('Одобрить промо'),
         on_click=approve,
         id='approve_promo'),
    Next(Const('Отклонить шаблоны'),
         id='reject'),
    SwitchTo(Const('Свой ответ'),
             id='custom_reject',
             state=AdminListening.custom),
    Back(Const('Назад'),
         on_click=cancel_task),
    state=AdminListening.info,
    getter=info_getter
)
