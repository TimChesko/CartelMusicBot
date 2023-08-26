from typing import Any

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start, Button
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.profile.personal_data.view.nickname import start_edit_nickname
from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.personal_data import PersonalDataHandler
from src.models.user import UserHandler
from src.utils.enums import Status
from src.utils.fsm import Profile, Passport, Bank, ProfileEdit, Social


async def get_data(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    personal_data = await PersonalDataHandler(data['session_maker'], data['database_logger']). \
        get_all_by_tg(user_id)
    user = await UserHandler(data['session_maker'], data['database_logger']).get_user_by_tg_id(user_id)
    status_dict = {
        Status.PROCESS: "🟡 на проверке",
        Status.REJECT: "⛔️ отклонены",
        Status.APPROVE: "✅ проверены",
    }
    passport = status_dict.get(personal_data.all_passport_data, "не имеются")
    bank = status_dict.get(personal_data.all_bank_data, "не имеются")

    return {
        "nickname": user.nickname,
        "status_passport": passport,
        "status_bank": bank,
        "edit_passport": personal_data.all_passport_data == Status.REJECT,
        "add_passport": personal_data.all_passport_data is None,
        "edit_bank": personal_data.all_bank_data == Status.REJECT,
        "add_bank": personal_data.all_bank_data is None
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
        Const("🙎‍♂️ <b>Профиль</b>\n"),
        Const("⚡ Мы ценим ваше время и желаем максимально упростить процесс сотрудничества с нашим лейблом. "
              "Создайте свой профиль всего <b>ОДИН РАЗ</b>, предоставив нам необходимые данные для оформления"
              " лицензионного договора, и дальше наслаждайтесь практически мгновенной публикацией ваших треков"
              " на популярных площадках!\n"),
        Const("🔒 <b>Ваша приватность - наш приоритет.</b> После оформления договора, все предоставленные вами данные "
              "удаляются. Мы гарантируем безопасность и конфиденциальность вашей информации.\n"),
        Format("Ваш псевдоним: <b>{nickname}</b>"),
        Format("Паспортные данные: <b>{status_passport}</b>"),
        Format("Банковские данные: <b>{status_bank}</b>"),
        Button(Const("📝 Изменить псевдоним"),
               id="profile_edit_nickname",
               on_click=edit_nickname),
        Button(Const("🔒 Изменить паспортные данные"),
               id="profile_edit_passport",
               when="edit_passport",
               on_click=edit_passport),
        Start(Const("🔒 Добавить паспортные данные"),
              id="profile_add_passport",
              when="add_passport",
              state=Passport.add_data),
        Button(Const("🏦 Изменить банковские данные"),
               id="profile_edit_bank",
               when="edit_bank",
               on_click=edit_bank),
        Start(Const("🏦 Добавить банковские данные"),
              id="profile_add_bank",
              when="add_bank",
              state=Bank.add_data),
        Start(Const("⭐️ Cоциальные сети"),
              id="profile_social",
              state=Social.view_data),
        BTN_CANCEL_BACK,
        state=Profile.menu,
        getter=get_data
    ),
    on_process_result=on_process
)
