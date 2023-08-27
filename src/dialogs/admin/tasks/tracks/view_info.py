from operator import itemgetter

from aiogram import Bot
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Button, ScrollingGroup, Multiselect, SwitchTo, Next, StubScroll, \
    NumberedPager
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.services.track_info_helper import get_struct_data, get_struct_text, get_struct_buttons, \
    get_checked_text, get_attachment_track
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_CONFIRM, TXT_REJECT, BTN_BACK, TXT_NEXT
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.track_info import TrackInfoHandler
from src.models.tracks import TrackHandler
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


async def get_data(dialog_manager: DialogManager, **_kwargs):
    return {
        "text": dialog_manager.dialog_data.get("converted_text")
    }


async def all_data(dialog_manager: DialogManager, **_kwargs):
    files = dialog_manager.dialog_data['files']
    track_id = dialog_manager.dialog_data['track_id']
    session_maker = dialog_manager.middleware_data['session_maker']
    database_logger = dialog_manager.middleware_data['database_logger']
    track_handler = TrackHandler(session_maker, database_logger)
    track = await track_handler.get_track_by_id(track_id)
    file_type, file_id = await get_attachment_track(dialog_manager, files, track, "stub_scroll_track_info_check")
    return {
        "pages": len(files.keys()) if files else 0,
        "attachment": MediaAttachment(file_type, file_id=MediaId(file_id))
    }


async def on_start(_, dialog_manager: DialogManager):
    await on_start_copy_start_data(None, dialog_manager)
    await dialog_manager.find("stub_scroll_track_info_check").set_page(0)
    middleware = dialog_manager.middleware_data
    docs = await (TrackInfoHandler(middleware['session_maker'], middleware['database_logger']).
                  get_docs_by_id(dialog_manager.dialog_data['track_id']))
    track = await (TrackHandler(middleware['session_maker'], middleware['database_logger']).
                   get_track_by_id(docs.track_id))
    files, text = await get_struct_data(docs)
    dialog_manager.dialog_data.update({
        'files': files,
        'text': text,
        'converted_text': await get_struct_text(text),
        'user_id': track.user_id
    })


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
    user_id = manager.dialog_data['user_id']
    comment = dialog_data.get("comment", None)
    await (TrackInfoHandler(middleware['session_maker'], middleware['database_logger']).
           set_status_reject(dialog_data['track_id'], dialog_data['result']))
    bot: Bot = middleware.get("bot", None)
    await bot.send_message(chat_id=user_id, text=f"❌ Документы к треку {dialog_data['text']['title']} отклонены !\n"
                                                 "Чтобы изменить данные к треку, перейдите в категорию \n"
                                                 f'"Моя студия" -> "Треки" -> "{dialog_data["text"]["title"]}" \n'
                                                 '-> "📝 Изменить данные"')
    if comment:
        await bot.send_message(chat_id=user_id, text=f"📝 Комментарий от модератора: \n{comment}")
    await manager.done()


async def on_approve(_, __, manager: DialogManager):
    middleware = manager.middleware_data
    dialog_data = manager.dialog_data
    user_id = manager.dialog_data['user_id']
    await (TrackInfoHandler(middleware['session_maker'], middleware['database_logger']).
           set_status_approve(dialog_data['track_id']))
    bot: Bot = middleware.get("bot", None)
    await bot.send_message(chat_id=user_id, text=f"✅ Документы к треку {dialog_data['text']['title']} приняты !\n"
                                                 f'"Главное меню" -> "Трек в продакшн"\n'
                                                 '🎵 Ваши творческие возможности ждут!')
    await manager.done()


async def set_comment(msg: Message, _, manager: DialogManager, __):
    manager.dialog_data['comment'] = msg.text
    await manager.next()


dialog = Dialog(
    Window(
        DynamicMedia('attachment'),
        StubScroll(id="stub_scroll_track_info_check", pages="pages"),
        NumberedPager(
            scroll="stub_scroll_track_info_check"
        ),
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
        DynamicMedia('attachment'),
        StubScroll(id="stub_scroll_track_info_check", pages="pages"),
        NumberedPager(
            scroll="stub_scroll_track_info_check"
        ),
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
        DynamicMedia('attachment'),
        StubScroll(id="stub_scroll_track_info_check", pages="pages"),
        NumberedPager(
            scroll="stub_scroll_track_info_check"
        ),
        Format("{finish_text}\n"),
        Const("Пришлите комментарий, который вы хотите оставить:"),
        TextInput(id="input_text_comment", on_success=set_comment),
        BTN_BACK,
        getter=get_finish_text,
        state=AdminCheckTrack.comment
    ),
    Window(
        DynamicMedia('attachment'),
        StubScroll(id="stub_scroll_track_info_check", pages="pages"),
        NumberedPager(
            scroll="stub_scroll_track_info_check"
        ),
        Format("{finish_text}"),
        Button(Const("✓ Закончить проверку"), id="finish", on_click=on_reject),
        BTN_BACK,
        state=AdminCheckTrack.finish,
        getter=get_finish_text
    ),
    getter=all_data,
    on_start=on_start,
    on_close=on_close
)
