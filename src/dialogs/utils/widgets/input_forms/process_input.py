import re
from typing import Any

from aiogram_dialog import DialogManager

from src.utils.fsm import Passport
from .window_input import start_dialog_filling_profile


class InputForm:

    def __init__(self, dialog_manager: DialogManager):
        self.manager = dialog_manager

    async def start_dialog(self,
                           btn_status: list[bool],
                           task_list: dict
                           ) -> None:
        """
        Запускает форму ввода.

        :param btn_status: Статус кнопок.
                           id: 0 - остановка формы.
                           id: 1 - назад при вводе текста.
                           id: 2 - назад при выборе даты.
        :param task_list: Список всех вопросов и ответов.
                          data_name: str - название данных.
                          text: str - вопрос в форме.
                          input: list - разрешенный тип данных.
        :return: None.
        """
        # Создаем список задач
        await self.__dialog_save_task_list(btn_status, task_list)
        # Запуск первой формы
        await start_dialog_filling_profile(*(await self.get_args()))

    async def get_args(self) -> tuple[list[bool], bool, bool, dict, DialogManager]:
        task_list = self.manager.dialog_data['task_list_all']
        key = self.manager.dialog_data["task_list_process"][0]
        input_date = True if "date" in task_list[key]['input_type'] else False
        input_img = True if "img" in task_list[key]['input_type'] else False
        btn_status = self.manager.dialog_data['btn_status']
        return btn_status, input_date, input_img, task_list[key], self.manager

    async def __dialog_save_task_list(self,
                                      btn_status: list[bool],
                                      task_list: dict,
                                      ) -> None:
        self.manager.dialog_data['btn_status'] = btn_status
        self.manager.dialog_data['save_input'] = {}
        self.manager.dialog_data['task_list_all'] = task_list
        self.manager.dialog_data['task_list_done'] = []
        self.manager.dialog_data["task_list_process"] = list(task_list.keys())

    @staticmethod
    async def validate_input(input_type: list[str], input_result: str) -> dict[Any, bool]:
        template_input = {
            "int": [r"\d{1,12}", "число до 12 цифр"],
            "big_int": [r"\d{1,24}", "число до 24 цифр"],
            "text": [r"a-zA-Zа-яА-Я", "буквы"],
            "punctuation": [r",.", "точки, запятые"],
            "minus": [r"-", "тире"],
            "space": [r"\s", "пробелы"],
            "any": [".*", "любые символы"],
            "date": [".*", "любые символы"],
            "img": [".*", "фотография"]
        }

        input_pattern = ''.join(template_input.get(item, [""])[0] for item in input_type)
        allowed_characters = ", ".join(template_input.get(item, ["", ""])[1] for item in input_type)

        if "any" in input_type:
            regex_pattern = rf'{input_pattern}$'
        elif ("big_int" in input_type or "int" in input_type) and "minus" in input_type:
            regex_pattern = rf'[{template_input["big_int"][0]}{template_input["minus"][0]}]+$'
        elif "big_int" in input_type or "int" in input_type:
            regex_pattern = rf'^{input_pattern}$'
        else:
            regex_pattern = rf'^[{input_pattern}]+$'

        if "img" in input_type or "date" in input_type or re.match(regex_pattern, input_result):
            return {"value": input_result, "check": True}
        else:
            return {"value": f"Ответ может содержать {allowed_characters}\nПовторите попытку снова", "check": False}


async def process_input_result(_, result: Any, manager: DialogManager):
    save_input = manager.dialog_data['save_input']
    task_list = manager.dialog_data['task_list_all']
    task_list_done = manager.dialog_data["task_list_done"]
    task_list_process = manager.dialog_data["task_list_process"]
    input_type = task_list[task_list_process[0]]['input_type']

    if "back" == result[0]:
        if len(task_list_done) != 0:
            task_list_process.insert(0, task_list_done.pop())
            await start_dialog_filling_profile(*(await InputForm(manager).get_args()))
        else:
            await manager.done()

    elif "task_list_process" in manager.dialog_data:
        validate = await InputForm(manager).validate_input(input_type, result[0])
        if validate['check']:
            old_item = task_list_process.pop(0)
            save_input[old_item] = {"value": result[0], "title": result[2], "data_name": result[1]}
            task_list_done.append(old_item)
            if len(manager.dialog_data["task_list_process"]) != 0:
                await start_dialog_filling_profile(*(await InputForm(manager).get_args()))
            else:
                await manager.next()
        else:
            await start_dialog_filling_profile(
                *(await InputForm(manager).get_args()),
                error=str(validate['value'])
            )
