from typing import Any

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel, Button
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.profile.personal_data.view.nickname import start_edit_nickname
from src.models.personal_data import PersonalDataHandler
from src.models.user import UserHandler
from src.utils.fsm import Profile, Passport, Bank, ProfileEdit, Social


async def get_data(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    passport_id, bank_id = await PersonalDataHandler(data['session_maker'], data['database_logger']).get_all_data_status(
        user_id)
    nickname = await UserHandler(data['session_maker'], data['database_logger']).get_user_nickname_by_tg_id(user_id)

    status_dict = {
        1: "🟡 на проверке",
        2: "⛔️ отклонены",
        3: "✅ проверены",
    }
    passport = status_dict.get(passport_id, "не имеются")
    bank = status_dict.get(bank_id, "не имеются")

    return {
        "nickname": nickname,
        "status_passport": passport,
        "status_bank": bank,
        "edit_passport": passport_id == 2,
        "add_passport": passport_id == 0,
        "edit_bank": bank_id == 2,
        "add_bank": bank_id == 0
    }


async def edit_passport(_, __, manager: DialogManager):
    await manager.start(state=ProfileEdit.menu, data={"header_data": "passport"})


async def edit_bank(_, __, manager: DialogManager):
    await manager.start(state=ProfileEdit.menu, data={"header_data": "bank"})


async def edit_nickname(_, __, manager: DialogManager):
    await start_edit_nickname(manager)


async def on_process(_, result: Any, manager: DialogManager):
    if result is not None and result[1] == "edit_nickname":
        data = manager.middleware_data
        user_id = data['event_from_user'].id
        await UserHandler(data['session_maker'], data['database_logger']).update_nickname(user_id, result[0])


menu = Dialog(
    Window(
        Format("Ваш псевдоним: {nickname}\n"
               "Паспортные данные: {status_passport}\n"
               "Банковские данные: {status_bank}"),
        Button(Const("Изменить псевдоним"),
               id="profile_edit_nickname",
               on_click=edit_nickname),
        Button(Const("Изменить паспортные данные"),
               id="profile_edit_passport",
               when="edit_passport",
               on_click=edit_passport),
        Start(Const("Добавить паспортные данные"),
              id="profile_add_passport",
              when="add_passport",
              state=Passport.add_data),
        Button(Const("Изменить банковские данные"),
               id="profile_edit_bank",
               when="edit_bank",
               on_click=edit_bank),
        Start(Const("Добавить банковские данные"),
              id="profile_add_bank",
              when="add_bank",
              state=Bank.add_data),
        Start(Const("Cоциальные сети"),
              id="profile_social",
              state=Social.view_data),
        Cancel(Const("Назад")),
        state=Profile.menu,
        getter=get_data
    ),
    on_process_result=on_process
)
