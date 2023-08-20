from operator import itemgetter

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.admin.tasks.personal_data.factory.process import CheckDocs, on_process
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, BTN_BACK
from src.models.personal_data import PersonalDataHandler
from src.models.user import UserHandler
from src.utils.enums import Status
from src.utils.fsm import AdminCheckPassport


async def formatting_docs(docs: list) -> list:
    new_docs = []
    for item in docs:
        text = f"{item.surname} {item.first_name}"
        new_docs.append([item.tg_id, text])
    return new_docs


async def get_data(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    docs = await PersonalDataHandler(data['session_maker'], data['database_logger']).get_docs_personal_data()
    docs = await formatting_docs(docs)
    return {
        "tasks": docs
    }


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    manager.dialog_data['user_id'] = int(selected_item)
    await manager.switch_to(AdminCheckPassport.view)


async def get_data_user(dialog_manager: DialogManager, **_kwargs):
    user_id = dialog_manager.dialog_data['user_id']
    data = dialog_manager.middleware_data
    user_data = await UserHandler(data['session_maker'], data['database_logger']).get_user_by_tg_id(user_id)
    user = await PersonalDataHandler(data['session_maker'], data['database_logger']).get_all_personal_data(user_id)
    passport = True if user.all_passport_data == Status.PROCESS else False
    bank = True if user.all_bank_data == Status.PROCESS else False
    return {
        "nickname": user_data.nickname,
        "user_id": user_id,
        "passport": passport,
        "bank": bank
    }


async def start_passport(_, __, manager: DialogManager):
    user_id = manager.dialog_data['user_id']
    await CheckDocs(manager, "passport").start_form(user_id)


async def start_bank(_, __, manager: DialogManager):
    user_id = manager.dialog_data['user_id']
    await CheckDocs(manager, "bank").start_form(user_id)


dialog = Dialog(
    Window(
        Const("Список данных на проверку"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="emp_document_list",
                items="tasks",
                item_id_getter=itemgetter(0),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_documents_with_pager',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        getter=get_data,
        state=AdminCheckPassport.menu
    ),
    Window(
        Format("Никнейм: <b>{nickname}</b>"),
        Format("Телеграм id: <code>{user_id}</code>\n"),
        Const("Выберете данные для проверки:"),
        Button(Const("Паспортные данные"), id="passport_data_check", on_click=start_passport, when="passport"),
        Button(Const("Банковские данные"), id="bank_data_check", on_click=start_bank, when="bank"),
        BTN_BACK,
        state=AdminCheckPassport.view,
        getter=get_data_user
    ),
    on_process_result=on_process
)
