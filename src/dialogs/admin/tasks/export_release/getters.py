from aiogram_dialog import DialogManager

from src.models.release import ReleaseHandler


async def release_list_getter(dialog_manager: DialogManager, **_kwargs):
    middleware = dialog_manager.middleware_data
    list_release_id = await (ReleaseHandler(middleware["session_maker"], middleware["database_logger"]).
                             get_list_export_release())
    return {
        "list_release": [[release[0].id] for release in list_release_id]
    }
