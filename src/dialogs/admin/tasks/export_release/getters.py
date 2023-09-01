from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId

from src.models.release import ReleaseHandler
from src.models.tables import Release, TrackInfo
from src.models.track_info import TrackInfoHandler
from src.models.tracks import TrackHandler


async def release_list_getter(dialog_manager: DialogManager, **_kwargs):
    middleware = dialog_manager.middleware_data
    database_args = (middleware["session_maker"], middleware["database_logger"])
    list_release_id = await ReleaseHandler(*database_args).get_list_export_release()
    return {
        "list_release": [[release[0].id] for release in list_release_id]
    }


async def get_attachment_release(manager: DialogManager, release: Release):
    current_page = int(await manager.find("release_stub_scroll").get_page())

    match current_page:
        case 0:
            return ContentType.DOCUMENT, release.release_cover, "обложка"
        case 1:
            return ContentType.DOCUMENT, release.signed_license, "лицензионный договор"
        case 2:
            return ContentType.PHOTO, release.mail_track_photo, "трек номер договора"
        case _:
            return None, None


async def tracks_list_getter(dialog_manager: DialogManager, **_kwargs):
    middleware = dialog_manager.middleware_data
    release_id = int(dialog_manager.dialog_data['release_id'])
    database_args = (middleware["session_maker"], middleware["database_logger"])
    release: Release = await ReleaseHandler(*database_args).get_release(release_id)
    list_tracks = await TrackHandler(*database_args).get_tracks_by_release(release_id)
    file_type, file_id, pick_file = await get_attachment_release(dialog_manager, release)
    if file_id is not None:
        file = MediaAttachment(file_type, file_id=MediaId(file_id))
    else:
        file = None
    return {
        "pick_file": pick_file,
        "release_title": release.release_title,
        "release_attachment": file,
        "release_pages": 3,
        "list_tracks": list_tracks
    }


async def create_text(track_info: TrackInfo) -> tuple[int, str]:
    pages = 2  # аудио + текст
    text = (f"Название: <code>{track_info.title}</code>\n"
            f"Автор слов: <code>{'да' if track_info.words_status else 'нет'}</code>\n")
    if not track_info.words_status:
        pages += 1
        text += f"ФИО автора текста: <code>{track_info.words_author_fullname}</code>\n"
    text += f"Автор бита: <code>{'да' if track_info.words_status else 'нет'}</code>\n"
    if not track_info.beat_status:
        pages += 1
        text += f"ФИО автора текста: <code>{track_info.beatmaker_fullname}</code>\n"
    text += f"Это фит: <code>{'да' if track_info.is_feat else 'нет'}</code>\n"
    if not track_info.is_feat:
        # TODO подставить ФИО, а не tg_id + вывод его ЛД
        text += (f"tg_id фитующего: <code>{track_info.feat_tg_id}</code>\n"
                 f"Процент фитующему: <code>{track_info.feat_percent}%</code>\n")
    text += (f"Время трека: <code>{track_info.tiktok_time}</code>\n"
             f"Присутствует мат: <code>{'да' if track_info.explicit_lyrics else 'нет'}</code>\n")
    return pages, text


async def get_attachment_track(manager, track_file_id, track_info: TrackInfo):
    current_page = int(await manager.find("track_stub_scroll").get_page())
    files = [track_file_id, track_info.text_file_id]
    if track_info.words_alienation:
        files.append(track_info.words_alienation)
    if track_info.beat_alienation:
        files.append(track_info.beat_alienation)
    file_id = files[current_page]
    if file_id == track_file_id:
        content_type = ContentType.AUDIO
    else:
        content_type = ContentType.DOCUMENT
    return content_type, file_id


async def track_getter(dialog_manager: DialogManager, **_kwargs):
    middleware = dialog_manager.middleware_data
    track_id = int(dialog_manager.dialog_data['track_id'])
    database_args = (middleware["session_maker"], middleware["database_logger"])
    file_id, track_info = await TrackInfoHandler(*database_args).get_docs_and_track(track_id)
    pages, text = await create_text(track_info)
    content_type, file_id = await get_attachment_track(dialog_manager, file_id, track_info)

    return {
        "track_pages": pages,
        "track_attachment": MediaAttachment(content_type, file_id=MediaId(file_id)),
        "text": text
    }
