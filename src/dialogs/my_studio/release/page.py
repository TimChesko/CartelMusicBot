import datetime
import os

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Group, Checkbox
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, List
from docxtpl import DocxTemplate

from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_BACK
from src.dialogs.utils.common import format_date
from src.models.release import ReleaseHandler
from src.models.personal_data import PersonalDataHandler
from src.models.tables import PersonalData
from src.utils.fsm import ReleaseTracks


async def set_release_mail(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_mail_track(
        manager.start_data['release_id'],
        msg.photo[0].file_id)
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.switch_to(ReleasePage.main)


async def other_type_handler_mail(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите трек номер в виде фото с сжатием")


mail = Window(
    Const("Прикрепите трек номер в виде фото с сжатием"),
    MessageInput(set_release_mail, content_types=[ContentType.PHOTO]),
    MessageInput(other_type_handler_mail),
    SwitchTo(TXT_BACK, 'from_mail', ReleasePage.main),
    state=ReleasePage.mail
)


async def other_type_handler_ld(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите лицензионный договор в виде файла")


async def set_release_ld(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_ld(manager.start_data['release_id'],
                                                                                msg.document.file_id)
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.switch_to(ReleasePage.main)


ld = Window(
    Const("Прикрепите лицензионное соглашение в виде документа"),
    MessageInput(set_release_ld, content_types=[ContentType.DOCUMENT]),
    MessageInput(other_type_handler_ld),
    SwitchTo(TXT_BACK, 'from_ld', ReleasePage.main),
    state=ReleasePage.ld
)


async def choose_track(__, _, manager: DialogManager):
    await manager.start(state=ReleaseTracks.start, data={'release_id': manager.start_data['release_id']},
                        show_mode=ShowMode.EDIT)


async def delete_release(__, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).delete_release(
        manager.start_data['release_id'])
    await manager.done()


async def on_approvement1lvl(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    personal: PersonalData = await PersonalDataHandler(data['session_maker'],
                                                       data['database_logger']).get_all_personal_data(
        callback.from_user.id)
    bot: Bot = data['bot']
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, 'files', 'template.docx')
    doc = DocxTemplate(file_path)
    context = {
        'licensor_name': f'{personal.surname} {personal.first_name[0]}.{personal.middle_name[0]}.',
        'name': f'{personal.surname} {personal.first_name} {personal.middle_name}',
        'inn_code': f'{personal.tin_self}',
        'passport': f'{personal.passport_series} {personal.passport_number}',
        'who_issued_it': f'{personal.who_issued_it}',
        'unit_code': f'{personal.unit_code}',
        'registration_address': f'{personal.registration_address}',
        'date_of_issue': f'{personal.date_of_issue}',
        'recipient': f'{personal.recipient}',
        'account_code': f'{personal.account_code}',
        'bank_recipient': f'{personal.bank_recipient}',
        'bik_code': f'{personal.bik_code}',
        'correct_code': f'{personal.correct_code}',
        'bank_inn_code': f'{personal.tin_bank}',
        'kpp_code': f'{personal.kpp_code}',
        'email': f'{personal.email}',
        'release_title': f'{personal}',
        'ld_number': f'{datetime.datetime.now().strftime("%d%m%Y%h%M%s")}',
        'date': f'{format_date()}',
    }
    temp_file = os.path.join(current_directory, 'files', f"{callback.from_user.id}.docx")
    doc.render(context)
    doc.save(temp_file)
    image_from_pc = FSInputFile(temp_file)
    msg = await callback.message.answer_document(image_from_pc)
    await bot.delete_message(callback.from_user.id, msg.message_id)
    await ReleaseHandler(data['session_maker'], data['database_logger']).update_unsigned_state(
        manager.start_data['release_id'],
        msg.document.file_id)
    os.remove(temp_file)


async def getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release, tracks = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release_scalar(
        dialog_manager.start_data['release_id'])
    is_cover = None
    if release.release_cover:
        doc_id = release.release_cover if dialog_manager.dialog_data['doc_state'] is True else release.unsigned_license
        is_cover = MediaAttachment(ContentType.DOCUMENT, file_id=MediaId(doc_id))
    return {
        'data': dialog_manager.start_data,
        'title': release.release_title if release.release_title else f'Новый альбом №{release.id}',
        'doc': is_cover,
        'tracks': tracks,
        'text_title': '✓ Название' if release.release_title else 'Дать название',
        'text_cover': '✓ Обложка' if release.release_cover else 'Прикрепить обложку',
        'text_tracks': '✓ Треки' if tracks else 'Прикрепить треки',
        'ld': '✓ Лиц. Договор' if release.signed_license else 'Лиц. Договор',
        'mail_track': '✓ Трек номер' if release.mail_track_photo else 'Трек номер',
        'when_clear': tracks is not None,
        'unsigned': not release.unsigned_state or release.unsigned_state == 'reject',
        'unsigned_when': all((release.release_title, release.release_cover, tracks)),
        'wait': release.unsigned_state == 'process' or release.signed_state == 'process' or release.mail_track_state == 'process',
        'signed': release.unsigned_state == 'approve' and not release.signed_state or release.signed_state == 'reject',
        'signed_when': release.signed_license is not None,
        'mail': release.signed_state == 'approve' and not release.mail_track_state or release.mail_track_state == 'reject',
        'mail_when': release.mail_track_photo is not None,
        'aggregate': release.mail_track_state == 'approve',
        'end': release.mail_track_state != 'approve'
    }


async def on_start(_, dialog_manager: DialogManager):
    dialog_manager.dialog_data['doc_state'] = True


async def change_state(_, __, manager: DialogManager):
    manager.dialog_data['doc_state'] = not manager.dialog_data['doc_state']


async def on_approvement2lvl(_, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).update_signed_state(
        manager.start_data['release_id'])


async def on_approvement3lvl(_, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).update_mail_state(
        manager.start_data['release_id'])


main = Dialog(
    Window(
        Format("Релиз: '{title}' \n Треки в релизе:"),
        List(Format('--- "{item.track_title}"'), items='tracks'),
        Const("\n ОЖИДАЙТЕ ПРОВЕРКУ", when='wait'),
        Const('Ваш трек находится на стадии отгрузки, ожидайте.', when='aggregate'),
        DynamicMedia('doc'),
        Group(
            SwitchTo(Format('{text_title}'), id='create_release_title', state=ReleasePage.title),
            SwitchTo(Format('{text_cover}'), id='create_release_cover', state=ReleasePage.cover),
            Button(Format('{text_tracks}'), id='add_tracks_to_release', on_click=choose_track),
            width=2,
            when='unsigned'
        ),
        Group(
            Button(Const('Очистить треки'), on_click=clear_tracks, id='clear_tracks', when='when_clear'),
            Button(Const('Отправить на проверку'), id='on_process_unsigned', on_click=on_approvement1lvl,
                   when='unsigned_when'),
            width=2,
            when='unsigned'
        ),
        Group(
            Checkbox(Const("🔘 Обложка/Договор"),
                     Const("Обложка/Договор 🔘"),
                     id='swap_docs',
                     on_click=change_state,
                     default=True),
            SwitchTo(Format('{ld}'), 'users_ld', state=ReleasePage.ld),
            Button(Const('Отправить на проверку'), id='on_process_signed', on_click=on_approvement2lvl,
                   when='signed_when'),
            when='signed'
        ),
        Group(
            Checkbox(Const("🔘 Обложка/Договор"),
                     Const("Обложка/Договор 🔘"),
                     id='swap_docs',
                     on_click=change_state,
                     default=True),
            SwitchTo(Format('{mail_track}'), 'users_mail', state=ReleasePage.mail),
            Button(Const('Отправить на проверку'), id='on_process_mail', on_click=on_approvement3lvl, when='mail_when'),
            when='mail'
        ),
        Button(Const('Удалить'), on_click=delete_release, id='delete_release', when='end'),
        BTN_CANCEL_BACK,
        state=ReleasePage.main,
        getter=getter
    ),
    title,
    cover,
    ld,
    mail,
    on_start=on_start
)
