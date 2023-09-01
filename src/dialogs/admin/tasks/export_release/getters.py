from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId

from src.models.release import ReleaseHandler
from src.models.tables import Release
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
        "attachment": file,
        "release_pages": 3,
        "list_tracks": list_tracks
    }


async def track_getter(dialog_manager: DialogManager, **_kwargs):
    return {}
