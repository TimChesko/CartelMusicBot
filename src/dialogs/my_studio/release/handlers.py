import logging
from io import BytesIO

from PIL import Image
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode

from src.models.release import ReleaseHandler
from src.models.tracks import TrackHandler
from src.utils.enums import Status
from src.utils.fsm import ReleaseTracks, ReleasePage1, ReleasePage2, ReleasePage3


async def on_release(_, __, manager: DialogManager, release_id):
    data = manager.middleware_data
    manager.dialog_data['release_id'] = release_id
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release(release_id)
    if all([release.signed_status is None, release.unsigned_status != Status.APPROVE]):
        await manager.start(ReleasePage1.main, data={'release_id': release_id}, show_mode=ShowMode.EDIT)
    elif all([release.mail_track_status is None, release.signed_status != Status.APPROVE]):
        await manager.start(ReleasePage2.main, data={'release_id': release_id}, show_mode=ShowMode.EDIT)
    elif all([release.signed_status == Status.APPROVE, release.mail_track_status != Status.APPROVE]):
        await manager.start(ReleasePage3.main, data={'release_id': release_id}, show_mode=ShowMode.EDIT)


async def create_release(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).add_new_release(callback.from_user.id)


async def clear_release_tracks(__, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).delete_release_id_from_tracks(
        manager.start_data['release_id'])


async def attach_tracks_to_release(__, _, manager: DialogManager):
    await manager.start(state=ReleaseTracks.start, data={'release_id': manager.start_data['release_id']},
                        show_mode=ShowMode.EDIT)


async def set_release_title(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_title(manager.start_data['release_id'],
                                                                                   msg.text)
    manager.start_data['title'] = msg.text
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.back()


async def release_title_oth(msg: Message, _, manager: DialogManager):
    await msg.delete()
    await msg.answer("Пришлите название альбома в виде сообщения")


async def set_release_cover(msg: Message, _, manager: DialogManager):
    manager.show_mode = ShowMode.EDIT
    logging.info(msg.document.thumbnail.file_size)
    logging.info(msg.document.thumbnail.width)
    if msg.document.thumbnail.width == msg.document.thumbnail.height:
        image = await msg.bot.download(msg.document.file_id, BytesIO())
        with Image.open(image) as img:
            width, height = img.size
        if width == 3000 and height == 3000:
            data = manager.middleware_data
            await ReleaseHandler(data['session_maker'], data['database_logger']).set_cover(
                manager.start_data['release_id'],
                msg.document.file_id)
            await msg.delete()
            await manager.switch_to(ReleasePage1.main)
    else:
        await msg.delete()
        manager.dialog_data[
            'error_cover'] = ("❗️<b>Пришлите обложку альбома в виде файла и"
                              " в соотношении сторон 1:1 расширением 3000х3000 пикселей(Высота=Ширина)</b>❗️")
        await manager.switch_to(ReleasePage1.cover)


# TODO переделать other type в одну функцию для всего блока
async def release_cover_oth(msg: Message, _, manager: DialogManager):
    await msg.delete()
    manager.dialog_data[
        'error_cover'] = ("❗️<b>Пришлите обложку альбома в виде файла и"
                          " в соотношении сторон 1:1 расширением 3000х3000 пикселей(Высота=Ширина)</b>❗️")
    manager.show_mode = ShowMode.EDIT


async def all_tracks_selected(__, _, manager: DialogManager):
    data = manager.middleware_data
    widget = manager.find('release_tracklist')
    tracklist = widget.get_checked()
    await TrackHandler(data['session_maker'], data['database_logger']).update_release_id(list(map(int, tracklist)),
                                                                                         manager.start_data[
                                                                                             'release_id'])
    await manager.done()


async def to_choose_tracks(__, _, manager: DialogManager):
    await manager.start(state=ReleaseTracks.start, data={'release_id': manager.start_data['release_id']},
                        show_mode=ShowMode.EDIT)


async def delete_release(__, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).delete_release(
        manager.start_data['release_id'])
    await manager.done()


async def release_ld_oth(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите лицензионный договор в виде файла")


async def set_release_ld(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_ld(manager.start_data['release_id'],
                                                                                msg.document.file_id)
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.switch_to(ReleasePage2.main)


async def on_approvement_lvl2(_, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).update_signed_state(
        manager.start_data['release_id'])


async def set_release_mail(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_mail_track(
        manager.start_data['release_id'],
        msg.photo[0].file_id)
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.switch_to(ReleasePage3.main)


async def release_mail_oth(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите трек номер в виде фото с сжатием")


async def on_approvement_lvl3(_, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).update_mail_state(
        manager.start_data['release_id'])
