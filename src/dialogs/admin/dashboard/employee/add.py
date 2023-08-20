from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Back
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.admin.common import translate_privilege
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, BTN_BACK, TXT_CONFIRM
from src.models.employee import EmployeeHandler
from src.models.tables import Employee
from src.models.user import UserHandler
from src.utils.enums import Privileges
from src.utils.fsm import AdminAddEmployee


async def employee_id(
        message: Message,
        _, manager: DialogManager):
    if message.text.isdigit():
        tg_id = int(message.text)
        data = manager.middleware_data
        config = data['config']
        employee: Employee = await EmployeeHandler(data['session_maker'],
                                                   data['database_logger']).get_privilege_by_tg_id(tg_id, config)
        if employee:
            await message.answer(f'Вы уже добавили сотрудника №{employee.tg_id}!')
        else:
            manager.dialog_data['employee_id'] = tg_id
            await message.delete()
            manager.show_mode = ShowMode.EDIT
            await manager.next()

    else:
        await message.answer('Telegram id может состоять только из цифр!')


async def incorrect_type(message: Message, _, __, ___):
    await message.delete()
    await message.answer('Некорректные данные, введите Telegram id')


async def set_privilege(_, button: Button, manager: DialogManager):
    manager.dialog_data['privilege'] = button.widget_id
    manager.dialog_data['status'] = button.text["text"].upper()
    await manager.next()


async def developer_getter(dialog_manager: DialogManager, **_kwargs):
    config = dialog_manager.middleware_data['config']
    user_id = dialog_manager.event.from_user.id
    return {
        'developer': user_id in config.constant.developers
    }


async def on_finish_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        'employee_id': dialog_manager.dialog_data['employee_id'],
        'privilege': dialog_manager.dialog_data['status']
    }


async def on_finish_privilege(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    user_id = manager.dialog_data['employee_id']
    user = await UserHandler(data['session_maker'], data['database_logger']).get_user_by_tg_id(user_id)
    if not user:
        await callback.answer('Ваш работник должен пройти первичную регистрацию по команде "/start"\n'
                              'На данный момент пользователь не найден!')
    else:
        privilege = manager.dialog_data['privilege']
        await EmployeeHandler(data['session_maker'], data['database_logger']).add_new_employee(callback, privilege)
        await manager.done()


new_employee = Dialog(
    Window(
        Const('Введите Telegram id работника'),
        MessageInput(employee_id,
                     content_types=[ContentType.TEXT],
                     # filter=F.text.isdigit()
                     ),
        BTN_CANCEL_BACK,
        state=AdminAddEmployee.start
    ),
    Window(
        Const('Выберите роль, которую хотите выдать данному юзеру:'),
        Button(Const('🧑‍💼Менеджер'),
               id=f'{Privileges.MANAGER}',
               on_click=set_privilege),
        Button(Const('👨🏼‍💻Модератор'),
               id=f'{Privileges.MODERATOR}',
               on_click=set_privilege),
        Button(Const('👨‍👦‍👦Куратор'),
               id=f'{Privileges.CURATOR}',
               on_click=set_privilege),
        Button(Const('🔐Администратор'),
               id=f'{Privileges.ADMIN}',
               on_click=set_privilege,
               when='developer'),
        BTN_BACK,
        state=AdminAddEmployee.privilege,
        getter=developer_getter
    ),
    Window(
        Format('Подтвердите действия Telegram ID: "{employee_id}"\n'
               'Статус: {privilege}'),
        Row(
            Button(TXT_CONFIRM, on_click=on_finish_privilege, id="approve_track"),
            Back(Const("Изменить"), id="edit_track"),
        ),
        BTN_CANCEL_BACK,
        state=AdminAddEmployee.finish,
        getter=on_finish_getter
    ),
)
