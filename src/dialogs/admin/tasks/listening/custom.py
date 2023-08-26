from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Back, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format

from src.dialogs.admin.tasks.listening.on_track import info_getter
from src.dialogs.utils.buttons import TXT_BACK, TXT_CONFIRM, TXT_EDIT
from src.models.tracks import TrackHandler
from src.utils.fsm import AdminListening


async def id_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        'id': dialog_manager.dialog_data['getter_info']['track_id']
    }


async def reason_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        'custom_reason': dialog_manager.dialog_data['reason']
    }


async def set_reject_reason(msg: Message, _, manager: DialogManager):
    manager.dialog_data["reason"] = msg.text
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.next()


async def other_type_handler_text(msg: Message, _, __):
    await msg.answer("Напишите причину в виде текста")


async def on_finish_custom_reason(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    info = manager.dialog_data['getter_info']
    track_id = manager.dialog_data['getter_info']['track_id']
    reason = manager.dialog_data['reason']
    await TrackHandler(data['session_maker'], data['database_logger']).update_checker(track_id, callback.from_user.id,
                                                                                      reason)
    await data['bot'].send_message(info['user_id'], f'Ваш трек <b>"{info["title"]}"</b>'
                                                    f' был отклонен с комментарием:\n {reason}.\n'
                                                    f'Не переживайте, вы можете внести изменения и'
                                                    f' отправить его на повторное прослушивание! 🎵🔧')
    await manager.done()


reason_window = Window(
    Format('❌ #{id} // Введи причину отказа'),
    DynamicMedia('audio'),
    MessageInput(set_reject_reason, content_types=[ContentType.TEXT]),
    MessageInput(other_type_handler_text),
    SwitchTo(TXT_BACK, state=AdminListening.info, id='bck_to_info'),
    state=AdminListening.custom,
    getter=(id_getter, info_getter)
)
confirm_reason_window = Window(
    Format('✅ Подтвердите текст:\n'
           '{custom_reason}'),
    DynamicMedia('audio'),
    Row(
        Button(TXT_CONFIRM, on_click=on_finish_custom_reason, id="approve_reason"),
        Back(TXT_EDIT, id="bck_reason"),
    ),
    SwitchTo(TXT_BACK, state=AdminListening.info, id='bck_to_info'),
    state=AdminListening.custom_confirm,
    getter=(reason_getter, info_getter)
)
