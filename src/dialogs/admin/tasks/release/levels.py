from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.admin.tasks.release.funcs import on_task_selected
from src.dialogs.admin.tasks.release.windows import create_task_info_window, create_reason_window, \
    create_reason_confirm_window
from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.release import ReleaseHandler
from src.utils.fsm import AdminReleaseLvl1, AdminReleaseLvl3, AdminReleaseLvl2


async def lvl1_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_unsigned_state('process')
    return {
        'release': release
    }


lvl1 = Dialog(
    Window(
        Const('Список тасков 1 уровень: \n'
              'Обложка + название + список треков + первичное ЛД'),
        ScrollingGroup(
            Select(
                Format("Релиз №{item.id}"),
                id="alb_adm_track_list",
                items="release",
                item_id_getter=lambda release: release.id,
                on_click=on_task_selected
            ),
            width=1,
            height=5,
            id='scroll_releases_lvl1',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminReleaseLvl1.start,
        getter=lvl1_getter
    ),
    create_task_info_window(AdminReleaseLvl1, 'unsigned'),
    create_reason_window(AdminReleaseLvl1),
    create_reason_confirm_window(AdminReleaseLvl1, 'unsigned')
)


async def lvl2_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_signed_state('process')
    return {
        'release': release
    }


lvl2 = Dialog(
    Window(
        Const('Список тасков 2 уровень: \n'
              'Подписанное ЛД, проверяй подпись'),
        ScrollingGroup(
            Select(
                Format("Релиз №{item.id}"),
                id="alb_adm_track_list",
                items="release",
                item_id_getter=lambda release: release.id,
                on_click=on_task_selected
            ),
            width=1,
            height=5,
            id='scroll_releases_lvl2',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminReleaseLvl2.start,
        getter=lvl2_getter
    ),
    create_task_info_window(AdminReleaseLvl2, 'signed'),
    create_reason_window(AdminReleaseLvl2),
    create_reason_confirm_window(AdminReleaseLvl2, 'signed')
)


async def lvl3_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_mail_state('process')
    return {
        'release': release
    }


lvl3 = Dialog(
    Window(
        Const('Список тасков 3 уровень: \n'
              'Трек номер с почты, проверяй фото и вбивай трек'),
        ScrollingGroup(
            Select(
                Format("Релиз №{item.id}"),
                id="alb_adm_track_list",
                items="release",
                item_id_getter=lambda release: release.id,
                on_click=on_task_selected
            ),
            width=1,
            height=5,
            id='scroll_releases_lvl3',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminReleaseLvl3.start,
        getter=lvl3_getter
    ),
    create_task_info_window(AdminReleaseLvl3, 'mail'),
    create_reason_window(AdminReleaseLvl3),
    create_reason_confirm_window(AdminReleaseLvl3, 'mail')
)
