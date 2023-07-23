import datetime
from operator import itemgetter

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Row, Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_CANCEL_BACK, BTN_BACK
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import AdminCheckPassport


async def formatting_docs(docs: list) -> list:
    new_docs = []
    for item in docs:
        text = f"{item.surname} {item.first_name}"
        new_docs.append([item.tg_id, text])
    return new_docs


async def get_data(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    docs = await PersonalDataHandler(data['session_maker'], data['database_logger']).get_docs_passport()
    docs = await formatting_docs(docs)
    return {
        "documents": docs
    }


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    data = manager.middleware_data
    answer = await PersonalDataHandler(data['session_maker'], data['database_logger']).passport_take_task()
    manager.dialog_data['selected_item'] = selected_item
    await manager.switch_to(AdminCheckPassport.view)


async def get_passport(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    selected_item = dialog_manager.dialog_data['selected_item']
    info = await PersonalDataHandler(data['session_maker'], data['database_logger']).get_data_by_tg(int(selected_item))
    text = f"Имя: {info.first_name}\n" \
           f"Фамилия: {info.surname}\n" \
           f"Отчество: {info.middle_name}\n\n" \
           f"Серия паспорта: {info.passport_series}\n" \
           f"Номер паспорта: {info.passport_number}\n" \
           f"Кем выдан: {info.who_issued_it}\n" \
           f"Когда выдан: {datetime.datetime.strftime(info.date_of_issue, '%d/%m/%Y')}\n" \
           f"Код подразделения: {info.unit_code}\n\n" \
           f"Дата рождения: {datetime.datetime.strftime(info.date_of_birth, '%d/%m/%Y')}\n" \
           f"Место рождения: {info.place_of_birth}\n" \
           f"Адрес регистрации: {info.registration_address}"
    dialog_manager.dialog_data['text'] = text
    return {"text": text}


dialog = Dialog(
    Window(
        Const("Список паспортных данных на проверку"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="emp_document_list",
                items="documents",
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
        Format("{text}"),
        Row(
            # SwitchTo(Const("Отклонить")),
            Button(Const("Принять"), id="passport_data_approve", on_click=...)
        ),
        BTN_BACK,
        getter=get_passport,
        state=AdminCheckPassport.view
    ),
)
