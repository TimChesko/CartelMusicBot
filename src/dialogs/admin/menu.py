from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.data.config import load_config
from src.dialogs.admin.common import privilege_level
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminMenu, AdminListening, AdminDashboard, AdminViewTypeDocs


async def privilege_getter(dialog_manager: DialogManager, **_kwargs):
    config = load_config()
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    privilege = await EmployeeHandler(data['session_maker'], data['database_logger']).get_privilege_by_tg_id(user_id,
                                                                                                             config)
    return privilege_level(config, privilege)


menu = Dialog(
    Window(
        Const('ГЛАВНОЕ МЕНЮ'),
        Start(Const('Прослушивание'),
              id='admin_listening',
              state=AdminListening.start,
              when='manager'),
        Start(Const('Проверка документов'),
              id='admin_documents',
              state=AdminViewTypeDocs.menu),
        Start(Const('Админ панель'),
              id='admin_panel',
              state=AdminDashboard.start,
              when='admin'),
        state=AdminMenu.start,
        getter=privilege_getter
    ),
)
