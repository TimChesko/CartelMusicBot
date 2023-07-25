import logging
from dataclasses import dataclass
from typing import Any

from adaptix import Retort
from aiogram_dialog import DialogManager

from src.dialogs.admin.tasks.personal_data.factory.window import start_dialog_check_docs
from src.models.comments_template import CommentsTemplateHandler
from src.models.personal_data import PersonalDataHandler


@dataclass
class ModelData:
    column_id: int
    header_name: str
    column_name: str
    title: str
    value: Any


async def create_all_task(manager: DialogManager, tg_id: int) -> list:
    middleware_ = manager.middleware_data
    big_data = await PersonalDataHandler(middleware_['session_maker'], middleware_['database_logger']). \
        get_specific_data(tg_id, ['passport', 'bank'])
    return big_data


async def get_all_answer(manager: DialogManager):
    middleware_ = manager.middleware_data
    return await CommentsTemplateHandler(middleware_['session_maker'], middleware_['database_logger']). \
        get_all_txt_template()


async def load_task_dialog(manager: DialogManager, tg_id: int):
    manager.dialog_data['all_task'] = await create_all_task(manager, tg_id)
    manager.dialog_data["old_task"] = []
    manager.dialog_data['photo'] = True
    manager.dialog_data['all_answer'] = await get_all_answer(manager)
    manager.dialog_data['comments'] = []


async def create_args(manager: DialogManager):
    dialog = manager.dialog_data
    task = dialog['all_task'].pop(0)
    data = {"task": task, "is_img": False}
    manager.dialog_data["old_task"].append(task)
    if data['task']['column_name'].startswith("photo"):
        data['is_img'] = True
    return data


async def start_view_personal_data(manager: DialogManager, tg_id: int):
    await load_task_dialog(manager, tg_id)
    data = await create_args(manager)
    await start_dialog_check_docs(manager, data=data)
