from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Cancel, Back
from aiogram_dialog.widgets.text import Format, Const

from src.models.user import UserHandler
from src.utils.fsm import Listening


async def get_music_file(message: Message, message_input: MessageInput, manager: DialogManager):
    if manager.is_preview():
        await manager.next()
        return
    manager.dialog_data["track"] = message.audio.file_id
    await manager.next()


async def other_type_handler(message: Message, message_input: MessageInput,
                             manager: DialogManager):
    await message.answer("Пришлите только сам трек")


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = (await dialog_manager.load_data())['middleware_data']
    user_nickname = await UserHandler(data['engine'], data['database_logger']) \
        .get_user_nickname(data['event_from_user'].id)
    return {
        "nickname": user_nickname,
    }


async def on_finish(callback: CallbackQuery, _, manager: DialogManager):
    # TODO отправить трек
    await callback.message.answer("Ваш трек отправлен на модерацию")
    manager.show_mode = ShowMode.SEND
    if manager.is_preview():
        await manager.done()
        return
    await manager.done()


dialog = Dialog(
    Window(
        Format("{nickname}, скиньте ваш трек"),
        MessageInput(get_music_file, content_types=[ContentType.AUDIO]),
        MessageInput(other_type_handler),
        state=Listening.start
    ),
    Window(
        Const("Подтверждение отправки данного трека"),
        Row(
            Button(Const("Подтверждаю"), on_click=on_finish, id="approve_track"),
            Back(Const("Изменить"), id="edit_track"),
        ),
        Cancel(Const("Вернуться в меню")),
        state=Listening.apply,
    ),
    getter=get_data,
)
