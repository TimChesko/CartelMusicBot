from operator import itemgetter

from aiogram import Bot
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Button, ScrollingGroup, Multiselect, SwitchTo, Next
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.services.track_info_helper import get_struct_data, get_struct_text, get_struct_buttons, \
    get_checked_text
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_CONFIRM, TXT_REJECT, BTN_BACK, TXT_NEXT
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.track_info import TrackInfoHandler
from src.utils.fsm import AdminCheckTrack


async def delete_messages(dialog_manager: DialogManager):
    bot = dialog_manager.middleware_data.get("bot", None)
    user_id = dialog_manager.middleware_data['event_from_user'].id
    message_ids = dialog_manager.dialog_data.get('send_msg', [])

    for message_id in message_ids:
        # noinspection PyBroadException
        try:
            await bot.delete_message(chat_id=user_id, message_id=message_id)
        except Exception:
            pass


async def on_close(_, dialog_manager: DialogManager):
    await delete_messages(dialog_manager)


async def send_files(dialog_manager: DialogManager, user_id: int, files: dict):
    middleware = dialog_manager.middleware_data
    bot = middleware.get("bot", None)

    if not bot:
        return False

    file_types = {
        "track_id": bot.send_audio,
        "text_file_id": bot.send_document,
        "beat_alienation": bot.send_document,
        "words_alienation": bot.send_document
    }

    dialog_manager.dialog_data['send_msg'] = []

    for file_key, send_method in file_types.items():
        file_data = files.get(file_key)
        if file_data:
            msg = await send_method(chat_id=user_id, **{file_key: file_data})
            dialog_manager.dialog_data['send_msg'].append(msg.message_id)
    return True


async def get_data(dialog_manager: DialogManager, **_kwargs):
    return {
        "text": dialog_manager.dialog_data.get("converted_text")
    }


async def on_start(_, dialog_manager: DialogManager):
    await on_start_copy_start_data(None, dialog_manager)
    middleware = dialog_manager.middleware_data
    user_id = dialog_manager.event.from_user.id
    docs = await (TrackInfoHandler(middleware['session_maker'], middleware['database_logger']).
                  get_docs_by_id(dialog_manager.dialog_data['track_id']))
    files, text = await get_struct_data(docs)
    dialog_manager.dialog_data.update({'files': files, 'text': text, 'converted_text': await get_struct_text(text)})
    await send_files(dialog_manager, user_id, files)
    dialog_manager.show_mode = ShowMode.SEND


async def get_buttons(dialog_manager: DialogManager, **_kwargs):
    dict_text = dialog_manager.dialog_data['text']
    return {
        "data": await get_struct_buttons(dict_text),
        "result": True if dialog_manager.find("ms_track").get_checked() else False
    }


async def on_pre_reject(_, __, manager: DialogManager):
    await manager.switch_to(AdminCheckTrack.finish)


async def get_finish_text(dialog_manager: DialogManager, **_kwargs):
    dict_text = dialog_manager.dialog_data.get("text")
    widget = dialog_manager.find("ms_track")
    dialog_manager.dialog_data['result'] = result = widget.get_checked()
    text = await get_checked_text(dict_text, result)
    return {
        "finish_text": text
    }


async def on_reject(_, __, manager: DialogManager):
    middleware = manager.middleware_data
    dialog_data = manager.dialog_data
    user_id = manager.event.from_user.id
    comment = dialog_data.get("comment", None)
    await (TrackInfoHandler(middleware['session_maker'], middleware['database_logger']).
           set_status_reject(dialog_data['track_id'], dialog_data['result'], comment))
    bot: Bot = middleware.get("bot", None)
    await bot.send_message(chat_id=user_id, text=f"Документы к треку {dialog_data['text']['title']} отклонены !")
    if comment:
        await bot.send_message(chat_id=user_id, text=f"Комментарий от модератора: \n{comment}")
    await manager.done()


async def on_approve(_, __, manager: DialogManager):
    middleware = manager.middleware_data
    dialog_data = manager.dialog_data
    user_id = manager.event.from_user.id
    await (TrackInfoHandler(middleware['session_maker'], middleware['database_logger']).
           set_status_approve(dialog_data['track_id']))
    bot: Bot = middleware.get("bot", None)
    await bot.send_message(chat_id=user_id, text=f"Документы к треку {dialog_data['text']['title']} приняты !")
    await manager.done()


async def set_comment(msg: Message, _, manager: DialogManager, __):
    manager.dialog_data['comment'] = msg.text
    await manager.next()


dialog = Dialog(
    Window(
        Const("Информация по треку\n"),
        Format("{text}"),
        Row(
            SwitchTo(TXT_REJECT, id="check_track_reject", state=AdminCheckTrack.reject_data),
            Button(TXT_CONFIRM, id="check_track_approve", on_click=on_approve),
        ),
        BTN_CANCEL_BACK,
        getter=get_data,
        state=AdminCheckTrack.menu,
    ),
    Window(
        Format("Выберете информацию, которую нужно отклонить:"),
        ScrollingGroup(
            Multiselect(
                Format("✓ {item[0]}"),
                Format("{item[0]}"),
                id="ms_track",
                items="data",
                item_id_getter=itemgetter(1),
            ),
            width=1,
            height=5,
            id="scroll_with_pager_personal_data",
            hide_on_single_page=True
        ),
        Next(Const("✍ Написать комментарий"), when='result'),
        Row(
            BTN_BACK,
            SwitchTo(TXT_NEXT, id="finish_check", state=AdminCheckTrack.finish),
        ),
        state=AdminCheckTrack.reject_data,
        getter=get_buttons
    ),
    Window(
        Format("{finish_text}\n"),
        Const("Пришлите комментарий, который вы хотите оставить:"),
        TextInput(id="input_text_comment", on_success=set_comment),
        BTN_BACK,
        getter=get_finish_text,
        state=AdminCheckTrack.comment
    ),
    Window(
        Format("{finish_text}"),
        Button(Const("✓ Закончить проверку"), id="finish", on_click=on_reject),
        BTN_BACK,
        state=AdminCheckTrack.finish,
        getter=get_finish_text
    ),
    on_start=on_start,
    on_close=on_close
)
