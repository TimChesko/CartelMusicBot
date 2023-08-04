from operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Back, ScrollingGroup, Select, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.listening.menu import tracks_getter
from src.dialogs.listening.new import other_type_handler_audio
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, BTN_BACK, TXT_BACK
from src.models.track import TrackHandler
from src.utils.fsm import ListeningEditTrack


async def on_item_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item: str):
    items = eval(selected_item)
    manager.dialog_data["track_id"] = int(items[1])
    manager.dialog_data['title'] = items[0]
    await manager.next()


async def on_finish_getter(dialog_manager: DialogManager, **_kwargs):
    file_id = dialog_manager.dialog_data['track'] if 'track' in dialog_manager.dialog_data else None
    title = dialog_manager.dialog_data['title']
    audio = MediaAttachment(ContentType.AUDIO, file_id=MediaId(file_id))
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
    await TrackHandler(data['session_maker'], data['database_logger']).update_edited_track(
        track_id=track_id,
        file_id_audio=manager.dialog_data["track"]
    )
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
                item_id_getter=itemgetter(0, 1),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        BTN_CANCEL_BACK,
        getter=tracks_getter,
        state=ListeningEditTrack.start,
    ),
    Window(
        Format("Скиньте новый файл трека {title}"),
        BTN_BACK,
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
        SwitchTo(Const(TXT_BACK), state=ListeningEditTrack.start, id='bck_to_list_start'),
        state=ListeningEditTrack.finish,
        getter=on_finish_getter
    ),
)
