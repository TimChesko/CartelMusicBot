import logging
from typing import Any

from aiogram_dialog import DialogManager, ShowMode

from src.dialogs.admin.tasks.personal_data.factory.window import start_dialog_check_docs
from src.models.comments_template import CommentsTemplateHandler
from src.models.personal_data import PersonalDataHandler
from src.models.personal_data_comment import PersonalDataCommentsHandler
from src.utils.fsm import PersonalDataCheck


async def create_all_task(manager: DialogManager, tg_id: int) -> list:
    middleware = manager.middleware_data
    big_data = await PersonalDataHandler(middleware['session_maker'], middleware['database_logger']). \
        get_specific_data(tg_id, ['passport', 'bank'])
    return big_data


async def get_all_answer(manager: DialogManager):
    middleware = manager.middleware_data
    return await CommentsTemplateHandler(middleware['session_maker'], middleware['database_logger']). \
        get_all_txt_template()


async def load_task_dialog(manager: DialogManager, tg_id: int):
    dialog = manager.dialog_data
    dialog['all_task'] = await create_all_task(manager, tg_id)
    dialog["old_task"] = []
    dialog['all_answer'] = await get_all_answer(manager)
    dialog['comments'] = {}
    dialog['edit'] = {}


async def create_args(task: dict, manager: DialogManager):
    dialog = manager.dialog_data
    data = {"task": task, "is_img": False}
    if data['task']['column_name'].startswith("photo"):
        data['is_img'] = True
        data['answers'] = dialog['all_answer']
    return data


async def start_view_personal_data(manager: DialogManager, tg_id: int):
    await load_task_dialog(manager, tg_id)
    await next_task(manager)


async def get_task(manager: DialogManager, next_turn: bool) -> dict:
    dialog = manager.dialog_data
    if next_turn:
        task = dialog["all_task"].pop(0)
        dialog['old_task'].append(task)
    else:
        if len(dialog["old_task"]) > 1:
            task_old = dialog["old_task"].pop()
            task = dialog["old_task"][-1]
            dialog['all_task'].insert(0, task_old)
        else:
            task = dialog["old_task"].pop()
            dialog['all_task'].insert(0, task)
    return task


async def next_task(manager: DialogManager):
    dialog = manager.dialog_data
    if len(dialog['all_task']) > 0:
        task = await get_task(manager, True)
        data = await create_args(task, manager)
        await start_dialog_check_docs(manager, data=data)
    else:
        await manager.start(state=PersonalDataCheck.finish)


async def back_task(manager: DialogManager):
    dialog = manager.dialog_data
    if len(dialog["old_task"]) > 0:
        task = await get_task(manager, False)
        data = await create_args(task, manager)
        await start_dialog_check_docs(manager, data=data)


async def on_process_check(_, result: Any, manager: DialogManager):
    manager.show_mode = ShowMode.EDIT
    if "finish" in result and result['finish']:
        middleware = manager.middleware_data
        user_id = manager.event.from_user.id
        # TODO провреить edit
        await PersonalDataHandler(middleware['session_maker'], middleware['database_logger']). \
            set_edit_data(user_id, manager.dialog_data['edit'])
        return await PersonalDataCommentsHandler(middleware['session_maker'], middleware['database_logger']). \
            set_comments(user_id, manager.dialog_data['comments'])
    elif "back" in result and result['back']:
        await back_task(manager)
    elif result['confirm']:
        if "stop" in result and result['stop']:
            middleware = manager.middleware_data
            user_id = manager.event.from_user.id
            return await PersonalDataCommentsHandler(middleware['session_maker'], middleware['database_logger']). \
                set_comments(user_id, manager.dialog_data['comments'])
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
