import logging

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Button, Row, Back
from aiogram_dialog.widgets.text import Const, Format

from src.data import config
from src.dialogs.admin.common import translate_privilege
from src.models.employee import EmployeeHandler
from src.models.user import UserHandler
from src.utils.fsm import AdminAddEmployee


async def employee_id(
        message: Message,
        message_input: MessageInput,
        manager: DialogManager):
    data = manager.middleware_data
    # user = await UserHandler(data['session_maker'], data['database_logger']).get_privilege_by_tg_id(message.from_user.id)
    # TODO заменить на запрос из employee
    # if user in config.PRIVILEGES[1:]:
    #     await message.delete()
    #     await message.answer('Вы уже добавили этого сотрудника!')
    #  TODO убрать комментарий, поменять второй условие на elif
    if message.text.isdigit():
        manager.dialog_data['employee_id'] = message.text
        await message.delete()
        manager.show_mode = ShowMode.EDIT
        await manager.next()
    else:
        await message.answer('Telegram id может состоять только из цифр!')


async def incorrect_type(message: Message,
                         widget: TextInput,
                         manager: DialogManager,
                         data):
    await message.delete()
    await message.answer('Некорректные данные, введите Telegram id')


async def set_privilege(callback: CallbackQuery, button: Button, manager: DialogManager):
    # manager.dialog_data['privilege_name'] = button.text
    manager.dialog_data['privilege'] = button.widget_id
    await manager.next()


async def developer_getter(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.middleware_data['event_from_user'].id
    logging.info(user_id)
    return {
        'developer': user_id in config.DEVELOPERS
    }


async def on_finish_getter(dialog_manager: DialogManager, **kwargs):
    return {
        'employee_id': dialog_manager.dialog_data['employee_id'],
        'privilege': translate_privilege(dialog_manager.dialog_data['privilege'])
    }


async def on_finish_privilege(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    user_id = int(manager.dialog_data['employee_id'])
    user = await UserHandler(data['session_maker'], data['database_logger']).check_user_by_tg_id(user_id)
    if not user:
        await callback.answer('Ваш работник должен пройти первичную регистрацию по команде "/start",\n'
                              ' на данный момент пользователь не найден!')
    else:
        privilege = manager.dialog_data['privilege']
        await EmployeeHandler(data['session_maker'], data['database_logger']).add_new_employee(user_id, privilege)
        await manager.done()


new_employee = Dialog(
    Window(
        Const('Введите Telegram id работника'),
        MessageInput(employee_id,
                     content_types=[ContentType.TEXT],
                     # filter=F.text.isdigit()
                     ),
        Cancel(Const('Назад')),
        state=AdminAddEmployee.start
    ),
    Window(
        Const('Выберите роль, которую хотите выдать данному юзеру:'),
        Button(Const('Менеджер'),
               id='manager',
               on_click=set_privilege),
        Button(Const('Модератор'),
               id='moderator',
               on_click=set_privilege),
        Button(Const('Куратор'),
               id='curator',
               on_click=set_privilege),
        Button(Const('Администратор'),
               id='admin',
               on_click=set_privilege,
               when='developer'),
        Back(),
        state=AdminAddEmployee.privilege,
        getter=developer_getter
    ),
    Window(
        Format('Подтвердите действия Telegram ID: "{employee_id}"\n'
               'Статус: {privilege}'),
        Row(
            Button(Const("Подтверждаю"), on_click=on_finish_privilege, id="approve_track"),
            Back(Const("Изменить"), id="edit_track"),
        ),
        Cancel(Const("Вернуться в главное меню")),
        state=AdminAddEmployee.finish,
        getter=on_finish_getter
    ),
)
