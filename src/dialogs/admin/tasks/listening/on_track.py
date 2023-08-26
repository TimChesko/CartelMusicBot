import logging
from _operator import itemgetter

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import SwitchTo, Back, Next, ScrollingGroup, Select
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import TXT_BACK, BTN_BACK
from src.models.listening_templates import ListeningTemplatesHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import AdminListening


async def info_getter(dialog_manager: DialogManager, **_kwargs):
    audio = MediaAttachment(ContentType.AUDIO, file_id=MediaId(dialog_manager.dialog_data['file']))
    return {
        **dialog_manager.dialog_data['getter_info'],
        'audio': audio
    }


async def on_item_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item):
    template_id = int(selected_item)
    data = manager.middleware_data
    bot: Bot = manager.middleware_data['bot']
    user_id = manager.dialog_data['getter_info']['user_id']
    track = await (ListeningTemplatesHandler(data['session_maker'], data['database_logger']).
                   get_all_scalar(type_name='reject', num_id=template_id))

    await callback.answer('Трек успешно отклонен!')
    await bot.send_message(chat_id=user_id, text=track.content)
    track_id = manager.dialog_data['getter_info']['track_id']
    await TrackHandler(data['session_maker'], data['database_logger']).update_checker(
        track_id, callback.from_user.id, track.content)
    await manager.switch_to(AdminListening.start)


async def reject_list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    track = await ListeningTemplatesHandler(data['session_maker'], data['database_logger']).get_all_all('reject')
    return {
        'rejects': track
    }


reject_templates = Window(
    Const('Выберите шаблон'),
    DynamicMedia('audio'),
    ScrollingGroup(
        Select(
            Format('"{item[1]}"'),
            id="temp_rej_list",
            items="rejects",
            item_id_getter=itemgetter(0),
            on_click=on_item_selected
        ),
        width=1,
        height=5,
        id='scroll_rejects_without_pager',
        hide_on_single_page=True
    ),
    BTN_BACK,
    state=AdminListening.templates,
    getter=(reject_list_getter, info_getter)
)


async def cancel_task(_, __, manager: DialogManager):
    data = manager.middleware_data
    track_id = manager.dialog_data['getter_info']['track_id']
    await TrackHandler(data['session_maker'], data['database_logger']).set_task_state(track_id, None)
    manager.show_mode = ShowMode.EDIT


async def approve(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    bot: Bot = data.get("bot", None)
    track_id = manager.dialog_data['getter_info']['track_id']
    user_id, title = await (TrackHandler(data['session_maker'], data['database_logger']).
                            update_approve(track_id, callback.from_user.id))
    await bot.send_message(chat_id=user_id,
                           text=f'Отличные новости! Ваш трек <b>"{title}"</b> '
                                f'успешно прошёл этап прослушивания. 🎧🎶\n'
                                f'Теперь пришло время поделиться вашим творчеством с аудиторией.\n'
                                f'Просто перейдите в раздел\n <b>"Моя студия"</b> ➡️ <b>"Мои треки"</b>'
                                f'и дополните информацию о треке в разделе <b>"Принятые"</b>.\n'
                                f' Этот важный шаг поможет выгрузить ваш трек на площадку и открыть его для мира! 🚀')


info_window = Window(
    Format('Уникальный номер: <code>{track_id}</code>'),
    Format('Название: <b>{title}</b>'),
    Format('Артист: <b>{nickname}</b> | {username}'),
    DynamicMedia('audio'),
    Back(Const('✓ Одобрить'),
         on_click=approve,
         id='approve'),
    # Next(Const('✓ Отклонить шаблоны'),
    #      id='reject'),
    SwitchTo(Const('✍ Свой ответ'),
             id='custom_reject',
             state=AdminListening.custom),
    Back(TXT_BACK, on_click=cancel_task),
    state=AdminListening.info,
    getter=info_getter
)
