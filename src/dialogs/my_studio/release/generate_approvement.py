import os
from datetime import datetime

from aiogram.types import FSInputFile
from docx.shared import Mm
from docxtpl import InlineImage, DocxTemplate

from src.models.personal_data import PersonalDataHandler
from src.models.release import ReleaseHandler


# async def on_approvement_lvl1(callback, _, manager):
#     data = manager.middleware_data
#     bot = data['bot']
#     session_maker = data['session_maker']
#     db_logger = data['database_logger']
#
#     track_info, release = await ReleaseHandler(session_maker, db_logger).get_track_with_release(
#         manager.start_data['release_id'])
#     current_directory = os.path.dirname(os.path.abspath(__file__))
#     cover_path = os.path.join(current_directory, 'files', f'{release.release_cover}.png')
#     file_path = os.path.join(current_directory, 'files', f'{len(track_info)}.docx')
#     doc = DocxTemplate(file_path)
#
#     featers = [callback.from_user.id]
#     await bot.download(release.release_cover, cover_path)
#     # Улучшил как смог, не получаем все значения User
#     info_featers = await PersonalDataHandler(session_maker, db_logger).get_personal_join_user(featers)
#
#     async def get_user_info():
#         for personal_data, nickname in info_featers:
#             yield personal_data, nickname
#
#     release_data = []
#     async for personal_data, nickname in get_user_info():
#         ld_file = os.path.join(current_directory, 'files', f"{nickname}{release.id}.docx")
#         doc.render(context_maker(personal_data, track_info, release, cover_path, doc, nickname))
#         doc.save(ld_file)
#         image_from_pc = FSInputFile(ld_file)
#         msg = await callback.message.answer_document(image_from_pc)
#         await bot.delete_message(callback.from_user.id, msg.message_id)
#         if personal_data.tg_id == callback.from_user.id:
#             release_data.append([True, manager.start_data['release_id'], msg.document.file_id])
#         else:
#             release_data.append([False, release, msg.document.file_id])
#         os.remove(ld_file)
#
#     # Время выполнения занесения 1 значения = 0.05 сек
#     await ReleaseHandler(session_maker, db_logger).add_or_update_unsigned_feat(release_data)
#     os.remove(cover_path)


def context_maker(personal, track_info, release, path, doc, nickname):
    fullname = f'{personal.surname} {personal.first_name} {personal.middle_name}'
    tiktok_time_split = track_info[0].tiktok_time.split(':')

    context = {
        'licensor_name': f'{personal.surname} {personal.first_name[0]}.{personal.middle_name[0]}.',
        'name': fullname,
        'nickname': nickname,
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
        'release_title': f'{release.release_title}',
        'ld_number': f'{datetime.now().strftime("%d%m%Y%")}-{release.id}',
        'date': f'{format_date()}',
        'year': datetime.now().strftime('%Y'),
        'cover': InlineImage(doc, path, width=Mm(100), height=Mm(100))
    }

    for number, track in enumerate(track_info):
        context[f'track_title{number}'] = track.title
        context[f'beat_author{number}'] = track.beatmaker_fullname if track.beatmaker_fullname else fullname
        context[f'words_author{number}'] = track.words_author_fullname if track.words_author_fullname else fullname
        context[f'min{number}'] = tiktok_time_split[0]
        context[f'sec{number}'] = tiktok_time_split[1]
        context[f'feat_percent{number}'] = track.feat_percent if track.feat_percent else '100'

    return context


def format_date(dt: datetime = None) -> str:
    if dt is None:
        dt = datetime.now()

    months_russian = {
        1: 'января',
        2: 'февраля',
        3: 'марта',
        4: 'апреля',
        5: 'мая',
        6: 'июня',
        7: 'июля',
        8: 'августа',
        9: 'сентября',
        10: 'октября',
        11: 'ноября',
        12: 'декабря'
    }

    day = dt.day
    month = months_russian[dt.month]
    year = dt.year

    return f'«{day}» {month} {year} г.'
