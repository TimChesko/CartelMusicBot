from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Row, Checkbox
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_NEXT, TXT_APPROVE, TXT_BACK
from src.dialogs.utils.widgets.input_forms.process_input import InputForm, process_input_result
from src.dialogs.utils.widgets.input_forms.utils import convert_data_types, get_data_from_db, get_key_value
from src.dialogs.utils.widgets.input_forms.window_input import start_dialog_filling_profile
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import Passport


async def create_form(_, __, manager: DialogManager):
    buttons = [False, True, True]
    task_list = await get_data_from_db("passport", manager)

    manager.show_mode = ShowMode.EDIT
    await InputForm(manager).start_dialog(buttons, task_list)


async def on_finally_passport(callback: CallbackQuery, _, manager: DialogManager):
    middleware_data = manager.middleware_data
    support = middleware_data['config'].constant.support
    user_id = manager.event.from_user.id
    data_values = await get_key_value(manager.dialog_data['save_input'])
    data = await convert_data_types(data_values)
    answer = await PersonalDataHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        update_all_personal_data(user_id, "passport", data)
    if answer:
        text = "✅ Вы успешно внесли данные о паспорте !"
    else:
        text = f'❌ Произошел сбой на стороне сервера. Обратитесь в поддержку {support}'
    await callback.message.delete()
    await middleware_data["bot"].send_message(chat_id=user_id, text=text)
    manager.show_mode = ShowMode.SEND
    await manager.done()


async def change_passport_img(_, __, manager: DialogManager):
    manager.dialog_data['img_state'] = not manager.dialog_data['img_state']


async def get_finish_data(dialog_manager: DialogManager, **_kwargs):
    text = ""
    list_photo = []
    for column, items in dialog_manager.dialog_data['save_input'].items():
        if items['data_name'].startswith("photo"):
            list_photo.append(items['value'])
        else:
            text += f"{items['title']}: <b>{items['value']}</b>\n"
    if "img_state" in dialog_manager.dialog_data:
        num_img = list_photo[0] if dialog_manager.dialog_data["img_state"] else list_photo[1]
    else:
        dialog_manager.dialog_data["img_state"] = True
        num_img = list_photo[0]
    img = MediaAttachment(ContentType.PHOTO, file_id=MediaId(num_img))
    return {
        "text": text,
        "passport": img,
    }


async def back_dialog(_, __, manager: DialogManager):
    task_list_done = manager.dialog_data["task_list_done"]
    task_list_process = manager.dialog_data["task_list_process"]
    manager.current_context().state = Passport.add_data
    if len(task_list_done) != 0:
        task_list_process.insert(0, task_list_done.pop())
        await start_dialog_filling_profile(*(await InputForm(manager).get_args()))
    else:
        await manager.done()


SWITCH_PHOTO = Checkbox(
    Const("1️⃣ / 2 страница"),
    Const("1 / 2️⃣ страница"),
    id="swap_passport",
    on_click=change_passport_img,
    default=True
)


add_full_data = Dialog(
    Window(
        Const("❇️ Перед началом заполнения данных, пожалуйста, подготовьте <b>паспорт</b>.\n"),
        Const("💠 За заполнением данных будет стоять две вещи:\n"
              "• прикрепление фотографий\n"
              "• ввод данных\n"),
        Const("❓ В дальнейшем ваши данные проверит один из модераторов и по ним будет создан лицензионный договор."),
        Row(
            BTN_CANCEL_BACK,
            Button(
                TXT_NEXT,
                id="passport_start",
                on_click=create_form
            ),
        ),
        state=Passport.add_data
    ),
    Window(
        DynamicMedia("passport"),
        Format("{text}"),
        SWITCH_PHOTO,
        Const("🔰 Проверьте и подтвердите правильность всех данных.\n"),
        Const("🔒 В целях безопасности, в дальнейшем у вас не будет возможности изменить или просмотреть"
              " внесенные данные без помощи модераторов."),
        Row(
            Button(TXT_BACK, id="passport_back", on_click=back_dialog),
            Button(TXT_APPROVE, id="passport_confirm", on_click=on_finally_passport),
        ),
        getter=get_finish_data,
        state=Passport.confirm
    ),
    on_process_result=process_input_result,
)
