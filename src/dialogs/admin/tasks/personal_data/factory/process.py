import logging
from typing import Any

from aiogram_dialog import DialogManager

from src.dialogs.admin.tasks.personal_data.factory.window import start_dialog_check_docs
from src.models.comments_template import CommentsTemplateHandler
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import PersonalDataCheck


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
    dialog = manager.dialog_data
    dialog['all_task'] = await create_all_task(manager, tg_id)
    dialog["old_task"] = []
    dialog['photo'] = True
    dialog['all_answer'] = await get_all_answer(manager)
    dialog['comments'] = {}
    dialog['edit'] = {}


async def create_args(manager: DialogManager):
    dialog = manager.dialog_data
    task = dialog['all_task'].pop(0)
    data = {"task": task, "is_img": False}
    dialog["old_task"].append(task)
    if data['task']['column_name'].startswith("photo"):
        data['is_img'] = True
    return data


async def undo_created_args(manager: DialogManager):
    dialog = manager.dialog_data
    task = dialog['old_task'].pop()
    dialog["all_task"].insert(0, task)


async def check_img_status(manager: DialogManager, data: dict):
    if not data['is_img'] and manager.dialog_data['photo']:
        manager.dialog_data['photo'] = False
        return False
    else:
        return True


async def start_view_personal_data(manager: DialogManager, tg_id: int):
    await load_task_dialog(manager, tg_id)
    data = await create_args(manager)
    status = await check_img_status(manager, data)
    if status:
        await start_dialog_check_docs(manager, data=data)
    else:
        await undo_created_args(manager)
        await manager.start(state=PersonalDataCheck.check_img)


async def next_task(manager: DialogManager):
    dialog = manager.dialog_data
    if len(dialog['all_task']) > 0:
        data = await create_args(manager)
        await start_dialog_check_docs(manager, data=data)
    else:
        await manager.start(state=PersonalDataCheck.finish)


async def back_task(manager: DialogManager):
    dialog = manager.dialog_data
    if len(dialog["old_task"]) > 1:
        task = dialog['old_task'].pop()
        dialog["all_task"].insert(0, task)
        data = {"task": task, "is_img": False}
        if data['task']['column_name'].startswith("photo"):
            data['is_img'] = True
            dialog['photo'] = True
        logging.debug(dialog["old_task"])
        logging.debug(data)
        await start_dialog_check_docs(manager, data=data)
    else:
        await manager.done()


async def on_process_check(_, result: Any, manager: DialogManager):
    if "finish" in result and result['back']:
        logging.debug(manager.dialog_data['edit'])
        logging.debug(manager.dialog_data['comments'])
    elif "back" in result and result['back']:
        await back_task(manager)
    elif result['confirm']:
        if "stop" in result and result['stop']:
            logging.debug(manager.dialog_data['edit'])
            logging.debug(manager.dialog_data['comments'])
        else:
            await next_task(manager)
    elif not result['confirm']:
        if result['edit'] is None:
            manager.dialog_data['comments'][result['column']] = result['comment']
        else:
            manager.dialog_data['edit'][result['column']] = result['edit']
        await next_task(manager)
    else:
        logging.debug("something wrong !!!")
