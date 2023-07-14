from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Back
from aiogram_dialog.widgets.text import Const

from src.dialogs.profile.personal_data import string
from src.dialogs.profile.personal_data.passport.process import start_dialog_filling_profile, process_input
from src.utils.fsm import Passport


async def on_finally_passport(callback: CallbackQuery, _, manager: DialogManager):
    await callback.answer("Вы успешно внесли данные о паспорте !")
    manager.show_mode = ShowMode.SEND
    await manager.done()


async def create_task_list(_, __, manager: DialogManager):
    all_data = string.passport
    tasks = []
    for i in all_data:
        tasks.append(i)
    manager.dialog_data["task_list_start"] = []
    manager.dialog_data["task_list_end"] = tasks
    await start_dialog_filling_profile(tasks[0], manager)


async def process_result(_, result: Any, manager: DialogManager):
    if "back" == result[0]:
        if len(manager.dialog_data["task_list_start"]) != 0:
            manager.dialog_data["task_list_end"].insert(0, manager.dialog_data["task_list_start"].pop())
            await start_dialog_filling_profile(manager.dialog_data["task_list_end"][0], manager)
        else:
            await manager.done()
    elif "task_list_end" in manager.dialog_data:
        all_data = string.passport
        await process_input(result, all_data[result[1]]['input'], manager)
    else:
        await manager.next()


passport = Dialog(
    Window(
        Const("Перед началом заполнения данных, подготовьте паспорт.\n"
              "Заполнение данных будет состоять из 2 этапов:\n"
              "- ввод данных\n"
              "- прикрепление фотографий"),
        Button(
            Const("Продолжить"),
            id="passport_start",
            on_click=create_task_list
        ),
        Cancel(Const("Вернуться в профиль")),
        state=Passport.add_data
    ),
    Window(
        Const("Проверьте и подтвердите правильность всех данных."
              "В целях безопасности, в дальнейшем у вас не будет возможности просмотреть"
              " внесенные данные без помощи модераторов."),
        Button(Const("Подтвердить"), id="passport_confirm", on_click=on_finally_passport),
        Back(Const("Назад")),
        state=Passport.confirm
    ),
    on_process_result=process_result,
)
