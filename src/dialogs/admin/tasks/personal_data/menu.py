from operator import itemgetter

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.admin.tasks.personal_data.factory.process import start_view_personal_data, on_process_check
from src.dialogs.utils.buttons import BTN_CANCEL_BACK
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
        "tasks": docs
    }


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    await start_view_personal_data(manager, int(selected_item))


dialog = Dialog(
    Window(
        Const("Список паспортных данных на проверку"),
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
    on_process_result=on_process_check
)
