from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Row, Cancel, Back, Checkbox
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const, List

from src.dialogs.admin.tasks.release.funcs import change_state, set_reject_reason, reason_title_getter, \
    task_page_getter, reject_release, clear_reason, reason_getter, confirm_release, cancel_task
from src.dialogs.utils import buttons
from src.dialogs.utils.buttons import TXT_BACK, TXT_CONFIRM, coming_soon
from src.utils.fsm import AdminReleaseLvl3, AdminReleaseLvl1, AdminReleaseLvl2

cover_or_ld = Checkbox(Const("🔘Обложка ⚪️Договор"),
                       Const("⚪️Обложка 🔘Договор"),
                       id='swap_docs',
                       on_click=change_state,
                       default=True,
                       when='checkbox')


def create_reason_window(state: [AdminReleaseLvl3 | AdminReleaseLvl2 | AdminReleaseLvl1]) -> Window:
    return Window(
        Format('{reason_title}'),
        DynamicMedia('doc'),
        cover_or_ld,
        MessageInput(set_reject_reason),
        SwitchTo(TXT_BACK, state=state.info, id='bck_to_info'),
        state=state.custom,
        getter=(reason_title_getter, task_page_getter)
    )


def create_reason_confirm_window(state: [AdminReleaseLvl3 | AdminReleaseLvl2 | AdminReleaseLvl1], id) -> Window:
    return Window(
        Format('Подтвердите текст:\n'
               '{custom_reason}'),
        DynamicMedia('doc'),
        cover_or_ld,
        Row(
            Cancel(buttons.TXT_APPROVE, on_click=reject_release, id=f"reason_{id}"),
            Back(buttons.TXT_EDIT, id="bck_reason", on_click=clear_reason),
        ),
        SwitchTo(TXT_BACK, state=state.info, id='bck_to_info', on_click=clear_reason),
        state=state.confirm,
        getter=(reason_getter, task_page_getter)
    )


def create_task_info_window(state: [AdminReleaseLvl3 | AdminReleaseLvl2 | AdminReleaseLvl1], id) -> Window:
    return Window(
        DynamicMedia('doc'),
        Format('Название релиза: <b>{title}</b>'),
        Format('Артист: {username} / {nickname}'),
        List(Format('{item.id})  "{item.track_title}"'), items='tracks'),
        cover_or_ld,
        Back(TXT_CONFIRM, id=f'confirm_{id}', on_click=confirm_release),
        # Back(TXT_REJECT, id=f'reject_{id}', on_click=reject_release),
        Button(Const('✘ Шаблон'), id=f'reject_release_template', on_click=coming_soon),
        SwitchTo(Const('✘ Свой ответ'), id=f'reject_release_custom', state=state.custom),
        Cancel(TXT_BACK, on_click=cancel_task),
        state=state.info,
        getter=task_page_getter
    )
