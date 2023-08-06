import logging
from operator import itemgetter

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Button, ScrollingGroup, Multiselect, SwitchTo, Next
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy.orm.state import InstanceState

from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_CONFIRM, TXT_REJECT, BTN_BACK
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.track_info import TrackInfoHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import AdminCheckTrack


async def on_close(_, dialog_manager: DialogManager):
    middleware = dialog_manager.middleware_data
    user_id = middleware['event_from_user'].id
    bot: Bot = middleware.get("bot", None)
    list_msg = dialog_manager.dialog_data['send_msg']
    for msg in list_msg:
        try:
            await bot.delete_message(chat_id=user_id, message_id=msg)
        except Exception:
            pass


async def get_struct_data(docs: dict):
    files, text = {}, {}
    for key, value in vars(docs).items():
        if not isinstance(value, InstanceState) and value is not None:
            if key in ("track_id", "text_file_id", "beat_alienation", "words_alienation"):
                files[key] = value
            elif key in template.keys():
                text[key] = value
    return files, text


template = {
    "title": "Название",
    "words_status": "Автор слов",
    "words_author_percent": "Процент автору слов",
    "beat_status": "Автор бита",
    "beatmaker_percent": "Процент автору бита",
    "feat_status": "Статус фита",
    "feat_tg_id": "Телеграм id на фите",
    "feat_percent": "Процент от фита",
    "tiktok_time": "Время трека",
    "explicit_lyrics": "Ненормативная лексика: "
}


async def create_text(text: dict):
    result = ""
    for key, value in text.items():
        result += f"{template[key]}: {value}\n"
    return result


async def send_files(dialog_manager: DialogManager, user_id: int, files: dict):
    middleware = dialog_manager.middleware_data
    dialog_data = dialog_manager.dialog_data
    bot: Bot = middleware.get("bot", None)
    if bot:
        dialog_data['send_msg'] = []
        if files.get("track_id"):
            track = await (TrackHandler(middleware['session_maker'], middleware['database_logger']).
                           get_track_by_id(files.get("track_id")))
            msg = await bot.send_audio(chat_id=user_id, audio=track.file_id_audio)
            dialog_data['send_msg'].append(msg.message_id)
        if files.get("text_file_id"):
            msg = await bot.send_document(chat_id=user_id, document=files.get("text_file_id"))
            dialog_data['send_msg'].append(msg.message_id)
        if files.get("beat_alienation"):
            msg = await bot.send_document(chat_id=user_id, document=files.get("beat_alienation"))
            dialog_data['send_msg'].append(msg.message_id)
        if files.get("words_alienation"):
            msg = await bot.send_document(chat_id=user_id, document=files.get("words_alienation"))
            dialog_data['send_msg'].append(msg.message_id)
        return True
    else:
        return False


async def get_data(dialog_manager: DialogManager, **_kwargs):
    return {
        "text": dialog_manager.dialog_data.get("converted_text")
    }


async def on_start(_, dialog_manager: DialogManager):
    await on_start_copy_start_data(None, dialog_manager)
    middleware = dialog_manager.middleware_data
    dialog_data = dialog_manager.dialog_data
    user_id = middleware['event_from_user'].id
    docs = await (TrackInfoHandler(middleware['session_maker'], middleware['database_logger']).
                  get_docs_by_id(dialog_data['track_id']))
    files, text = await get_struct_data(docs)
    dialog_data['files'] = files
    dialog_data['text'] = text
    dialog_data['converted_text'] = await create_text(text)
    await send_files(dialog_manager, user_id, files)
    dialog_manager.show_mode = ShowMode.SEND


async def get_buttons(dialog_manager: DialogManager, **_kwargs):
    dict_text = dialog_manager.dialog_data['text']
    buttons = []
    for key in dict_text.keys():
        buttons.append([template[key], key])
    return {
        "data": buttons,
        "result": True if dialog_manager.find("ms_track").get_checked() else False
    }


async def on_pre_reject(_, __, manager: DialogManager):
    await manager.switch_to(AdminCheckTrack.finish)


async def get_finish_text(dialog_manager: DialogManager, **_kwargs):
    dict_text = dialog_manager.dialog_data.get("text")
    widget = dialog_manager.find("ms_track")
    dialog_manager.dialog_data['result'] = result = widget.get_checked()
    text = ""
    for key in dict_text.keys():
        if key in result:
            text += f"❌ {template[key]}: {dict_text[key]}\n"
        else:
            text += f"{template[key]}: {dict_text[key]}\n"
    return {
        "finish_text": text
    }


async def on_reject(_, __, manager: DialogManager):
    middleware = manager.middleware_data
    dialog_data = manager.dialog_data
    user_id = middleware['event_from_user'].id
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
    user_id = middleware['event_from_user'].id
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
            SwitchTo(Const(TXT_REJECT), id="check_track_reject", state=AdminCheckTrack.reject_data),
            Button(Const(TXT_CONFIRM), id="check_track_approve", on_click=on_approve),
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
        Next(Const("Написать комментарий"), when='result'),
        Row(
            BTN_BACK,
            SwitchTo(Const("Продолжить"), id="finish_check", state=AdminCheckTrack.finish),
        ),
        state=AdminCheckTrack.reject_data,
        getter=get_buttons
    ),
    Window(
        Format("{finish_text}"),
        Const("\nПришлите комментарий, который вы хотите оставить:"),
        TextInput(id="input_text_comment", on_success=set_comment),
        BTN_BACK,
        getter=get_finish_text,
        state=AdminCheckTrack.comment
    ),
    Window(
        Format("{finish_text}"),
        Button(Const("Закончить проверку"), id="finish", on_click=on_reject),
        BTN_BACK,
        state=AdminCheckTrack.finish,
        getter=get_finish_text
    ),
    on_start=on_start,
    on_close=on_close
)
