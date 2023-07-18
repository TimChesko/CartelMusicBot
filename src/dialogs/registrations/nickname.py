from aiogram.types import CallbackQuery, ContentType, Message
from aiogram_dialog import (
    Dialog, DialogManager, Window, StartMode, ShowMode,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Row
from aiogram_dialog.widgets.text import Const, Format, Multi

from src.models.personal_data import PersonalDataHandler
from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu


async def get_data(dialog_manager: DialogManager, **kwargs):
    return {
        "nickname": dialog_manager.dialog_data['nickname']
    }


async def nickname_check(msg: Message, _, manager: DialogManager):
    manager.dialog_data["nickname"] = msg.text
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.next()


async def on_finish(callback: CallbackQuery, _, manager: DialogManager):
    data = (await manager.load_data())['middleware_data']
    nickname = manager.dialog_data['nickname']
    await UserHandler(data['session_maker'], data['database_logger']).set_user_nickname(
        callback.from_user.id, nickname)
    await PersonalDataHandler(data['session_maker'], data['database_logger']).create_row(callback.from_user.id)
    await callback.message.answer("Спасибо за регистрацию ❤️")
    await manager.start(StartMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)


reg_nickname = Dialog(
    Window(
        Const("Перед использованием бота, введите свой псевдоним:"),
        MessageInput(nickname_check, content_types=[ContentType.TEXT]),
        state=RegNickname.nickname
    ),
    Window(
        Multi(
            Format("Ваш псевдоним: {nickname}")
        ),
        Row(
            Back(Const("Изменить")),
            Button(Const("Продолжить"), on_click=on_finish, id="finish"),
        ),
        getter=get_data,
        state=RegNickname.finish
    )
)
