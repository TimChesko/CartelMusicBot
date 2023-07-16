import logging

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.data import config
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.employee import EmployeeHandler
from src.models.user import UserHandler
from src.utils.fsm import AdminMenu, AdminListening, AdminDashboardPIN, AdminDashboard


async def privilege_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    privilege = await EmployeeHandler(data['engine'], data['database_logger']).get_privilege_by_tg_id(user_id)
    if user_id in config.DEVELOPERS:
        return {
            privilege: True for privilege in config.PRIVILEGES
        }
    user_privilege_index = config.PRIVILEGES.index(privilege)
    # TODO доделать под список только из модераторов
    return {
        privilege: user_privilege_index >= config.PRIVILEGES.index(privilege) for privilege in config.PRIVILEGES
    }


admin_main = Dialog(
    Window(
        Const('ГЛАВНОЕ МЕНЮ'),
        Start(Const('Прослушивание'),
              id='admin_listening',
              state=AdminListening.start,
              when='manager'),
        Start(Const('Админ панель'),
              id='admin_panel',
              state=AdminDashboardPIN.start,
              when='admin'),
        state=AdminMenu.start,
        getter=privilege_getter
    ),
)
