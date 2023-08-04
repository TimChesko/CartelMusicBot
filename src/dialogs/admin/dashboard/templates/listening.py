import logging
from _operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Button, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import TXT_BACK, BTN_CANCEL_BACK
from src.models.listening_templates import ListeningTemplatesHandler
from src.utils.fsm import TemplatesListening


async def add_content(message: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ListeningTemplatesHandler(data['session_maker'], data['database_logger']).add_reject(
        manager.dialog_data['new_name'],
        message.text)
    await message.delete()
    await message.answer(f'Шаблон "{manager.dialog_data["new_name"]}" успешно добавлен!')
    await manager.switch_to(TemplatesListening.reject)


add_new_content = Window(
    Const('Введите текст для шаблона'),
    MessageInput(add_content, content_types=[ContentType.TEXT]),
    SwitchTo(Const(TXT_BACK), id='bck_to_menu', state=TemplatesListening.start),
    state=TemplatesListening.add_content
)


async def add_name(message: Message, _, manager: DialogManager):
    manager.dialog_data['new_name'] = message.text
    await message.delete()
    await manager.switch_to(TemplatesListening.add_content)


add_new_name = Window(
    Const('Введите название для шаблона'),
    MessageInput(add_name, content_types=[ContentType.TEXT]),
    SwitchTo(Const(TXT_BACK), id='bck_to_menu', state=TemplatesListening.start),
    state=TemplatesListening.add_name
)


async def update_content(message: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ListeningTemplatesHandler(data['session_maker'], data['database_logger']).update_content(
        manager.dialog_data['type'],
        message.text)
    await message.delete()
    await message.answer('Текст шаблона успешно сменён!')
    await manager.switch_to(TemplatesListening.info)


async def update_name(message: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ListeningTemplatesHandler(data['session_maker'], data['database_logger']).update_name(
        manager.dialog_data['type'],
        message.text)
    await message.delete()
    await message.answer('Название шаблона успешно сменено!')
    await manager.switch_to(TemplatesListening.info)


name_input = Window(
    Const('Введите новое название для шаблона'),
    MessageInput(update_name, content_types=[ContentType.TEXT]),
    SwitchTo(Const(TXT_BACK), id='bck_to_menu', state=TemplatesListening.start),
    state=TemplatesListening.name
)

content_input = Window(
    Const('Введите новый текст для шаблона'),
    MessageInput(update_content, content_types=[ContentType.TEXT]),
    SwitchTo(Const(TXT_BACK), id='bck_to_menu', state=TemplatesListening.start),
    state=TemplatesListening.content
)


async def reject_list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    track = await ListeningTemplatesHandler(data['session_maker'], data['database_logger']).get_all_all(
        dialog_manager.dialog_data['type'])
    return {
        'rejects': track
    }


async def on_item_selected(_, __, manager: DialogManager, selected_item):
    manager.dialog_data['temp_id'] = int(selected_item)
    await manager.switch_to(TemplatesListening.info)


rejects_list = Window(
    Const('Список треков на прослушивание'),
    ScrollingGroup(
        Select(
            Format('"{item[1]}"'),
            id="temp_rej_list",
            items="rejects",
            item_id_getter=itemgetter(0),
            on_click=on_item_selected
        ),
        width=1,
        height=5,
        id='scroll_rejects_with_pager',
        hide_on_single_page=True
    ),
    SwitchTo(Const('Добавить'), id='add', state=TemplatesListening.add_name),
    SwitchTo(Const(TXT_BACK), id='bck_to_menu', state=TemplatesListening.start),
    state=TemplatesListening.reject,
    getter=reject_list_getter
)


async def info_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    id = dialog_manager.dialog_data['temp_id'] if 'temp_id' in dialog_manager.dialog_data else None
    reason = await ListeningTemplatesHandler(data['session_maker'], data['database_logger']).get_all_scalar(
        dialog_manager.dialog_data['type'], id)
    logging.info(reason)
    return {
        'name': reason.name,
        'content': reason.content,
        'rejected': reason.type == 'reject'
    }


async def to_next(_, btn: Button, manager: DialogManager):
    manager.dialog_data['type'] = btn.widget_id


async def del_data(_, __, manager: DialogManager):
    manager.dialog_data.clear()


async def del_reject(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.middleware_data
    await ListeningTemplatesHandler(data['session_maker'], data['database_logger']).delete_template(
        manager.dialog_data['temp_id'])
    await callback.answer('Шаблон успешно удален!')
    manager.dialog_data.clear()


info = Window(
    Format('Название: {name}\n'
           'Текст:\n{content}'),
    SwitchTo(Const('Изменить текст'), id='change_content', state=TemplatesListening.content),
    SwitchTo(Const('Изменить название'), id='change_name', state=TemplatesListening.name, when='rejected'),
    SwitchTo(Const('Удалить'), id='delete_rej', state=TemplatesListening.start, on_click=del_reject, when='rejected'),
    SwitchTo(Const(TXT_BACK), id='bck_to_menu', state=TemplatesListening.start, on_click=del_data),
    state=TemplatesListening.info,
    getter=info_getter
)

choice = Dialog(
    Window(
        Const('Выберите шаблон, который хотите изменить'),
        SwitchTo(Const('Одобрить'),
                 id='approve',
                 on_click=to_next,
                 state=TemplatesListening.info),
        SwitchTo(Const('Одобрить с промо'),
                 id='approve_promo',
                 on_click=to_next,
                 state=TemplatesListening.info),
        SwitchTo(Const('Отклонения'),
                 id='reject',
                 on_click=to_next,
                 state=TemplatesListening.reject),
        BTN_CANCEL_BACK,
        state=TemplatesListening.start
    ),
    info,
    content_input,
    name_input,
    rejects_list,
    add_new_name,
    add_new_content
)
