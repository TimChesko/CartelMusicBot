import dataclasses
import logging
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.dialogs.admin.tasks.personal_data.factory.window import start_dialog_check_docs
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import AdminCheckPassport


@dataclasses.dataclass
class Task:
    column_id: int
    column_name: str
    title: str
    value: str


class CheckDocs:

    def __init__(self,
                 manager: DialogManager,
                 header_name: str
                 ):
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
        dialog['del_id_msg'] = []

    @staticmethod
    async def __find_photo(big_data: list[dict]):
        list_photo, list_text = [], []
        for item in big_data:
            converted_item = Task(*item.values())
            if converted_item.column_name.startswith("photo"):
                list_photo.append(item)
            else:
                list_text.append(item)
        return list_photo if list_photo else None, list_text

    async def __load_form(self, user_id: int):
        big_data = await self.__get_all_task(user_id)
        await self.__upload_dialog_data(user_id, big_data)
        photo, text = await self.__find_photo(big_data)
        return photo, text

    async def start_form(self, user_id: int, callback: CallbackQuery = None):
        photo, text = await self.__load_form(user_id)
        await start_dialog_check_docs(self.manager, text, photo, callback)


async def calc_exit(manager: DialogManager):
    middleware = manager.middleware_data
    user_id = manager.dialog_data['user_id']
    personal_data = PersonalDataHandler(middleware['session_maker'], middleware['database_logger'])
    user = await personal_data.get_all_personal_data(user_id)
    if user.all_passport_data == "process" or user.all_bank_data == "process":
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
