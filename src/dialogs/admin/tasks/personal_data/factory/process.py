from typing import Any

from aiogram_dialog import DialogManager

from src.dialogs.admin.tasks.personal_data.factory.model import Task
from src.dialogs.admin.tasks.personal_data.factory.window import start_dialog_check_docs
from src.models.personal_data import PersonalDataHandler
from src.utils.enums import Status
from src.utils.fsm import AdminCheckPassport


class CheckDocs:

    def __init__(self, manager: DialogManager, header_name: str):
        self.manager = manager
        self.header_name = header_name

    async def __get_all_task(self, user_id: int) -> list:
        middleware = self.manager.middleware_data
        big_data = await PersonalDataHandler(middleware['session_maker'], middleware['database_logger']). \
            get_specific_data(user_id, self.header_name)
        return big_data

    async def __upload_dialog_data(self, user_id: int, big_data: list):
        dialog = self.manager.dialog_data
        dialog['user_id'] = user_id
        dialog['header_name'] = self.header_name
        dialog['all_data'] = big_data

    async def load_form(self, user_id: int):
        big_data = await self.__get_all_task(user_id)
        await self.__upload_dialog_data(user_id, big_data)
        photo, text = await find_photo_and_text(big_data)
        return photo, text

    async def start_form(self, user_id: int):
        photo, text = await self.load_form(user_id)
        await start_dialog_check_docs(self.manager, text, photo)


async def find_photo_and_text(big_data: list[dict]):
    list_photo, list_text = [], []
    for item in big_data:
        converted_item = Task(*item.values())
        if converted_item.column_name.startswith("photo"):
            list_photo.append(item)
        else:
            list_text.append(item)
    return list_photo if list_photo else None, list_text


async def calc_exit(manager: DialogManager):
    middleware = manager.middleware_data
    user_id = manager.dialog_data['user_id']
    personal_data = PersonalDataHandler(middleware['session_maker'], middleware['database_logger'])
    user = await personal_data.get_all_personal_data(user_id)
    if user.all_passport_data == Status.PROCESS or user.all_bank_data == Status.PROCESS:
        return await manager.switch_to(AdminCheckPassport.view)
    count = await personal_data.get_docs_count_personal_data()
    if count and count > 0:
        return await manager.switch_to(AdminCheckPassport.menu)
    return await manager.done()


async def on_process(_, result: Any, manager: DialogManager):
    middleware = manager.middleware_data
    user_id = manager.dialog_data['user_id']
    header_name = manager.dialog_data['header_name']
    if result.get("confirm"):
        await PersonalDataHandler(middleware['session_maker'], middleware['database_logger']). \
            set_confirm_personal_data(user_id, header_name)
    elif result.get("edit"):
        await PersonalDataHandler(middleware['session_maker'], middleware['database_logger']). \
            set_reject_dict(user_id, header_name, result['edit'])
    await calc_exit(manager)
