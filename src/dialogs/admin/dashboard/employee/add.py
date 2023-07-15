from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, LaunchMode, DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Start, Cancel, Button, Row, Back
from aiogram_dialog.widgets.text import Const, Format

from src.data import config
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.user import UserHandler
from src.utils.fsm import AdminMenu, AdminListening, AdminDashboardPIN, AdminDashboard, AdminEmployee, AdminAddEmployee


async def employee_id(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        data):
    if data.isdigit():
        manager.dialog_data['employee_id'] = data
        await message.delete()
        await manager.next()
    else:
        await message.delete()
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
    return {
        'developer': user_id in config.DEVELOPERS
    }


async def on_finish_getter(dialog_manager: DialogManager, **kwargs):
    return {
        'employee_id': dialog_manager.dialog_data['employee_id'],
        'privilege': dialog_manager.dialog_data['privilege']
    }


async def on_finish_privilege(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    user_id = int(manager.dialog_data['employee_id'])
    privilege = manager.dialog_data['privilege']
    user = await UserHandler(data['engine'], data['database_logger']).check_user_by_tg_id(user_id)
    if not user:
        await callback.answer('Ваш работник должен пройти первичную регистрацию по команде "/start",\n'
                              ' на данный момент пользователь не найден!')
    else:
        await UserHandler(data['engine'], data['database_logger']).set_privilege(user_id, privilege)
        await manager.done()


new_employee = Dialog(
    Window(
        Const('Введите Telegram id работника'),
        TextInput(id='employee_id',
                  on_success=employee_id,
                  on_error=incorrect_type),
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
