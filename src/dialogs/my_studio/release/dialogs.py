from _operator import itemgetter

from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Group
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Multiselect
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, List, Multi

from src.dialogs.my_studio.release.generate_approvement import on_approvement_lvl1
from src.dialogs.my_studio.release.getters import create_new_release_getter, lvl1_getter, choose_tracks_getter, \
    lvl2_getter, lvl3_getter, cover_getter
from src.dialogs.my_studio.release.handlers import create_release, on_release, clear_release_tracks, set_release_title, \
    release_title_oth, set_release_cover, release_cover_oth, all_tracks_selected, to_choose_tracks, \
    delete_release, release_ld_oth, set_release_ld, on_approvement_lvl2, release_mail_oth, set_release_mail, \
    on_approvement_lvl3
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_BACK
from src.utils.fsm import ReleaseTrack, ReleasePage1, ReleasePage2, ReleasePage3
from src.utils.fsm import ReleaseTracks

delete = Button(Const('Удалить'), on_click=delete_release, id='delete_release')

release_info = Multi(
    Format('Релиз: <b>"{title}"</b>'),
    Const('Треки в релизе:'),
    List(Format('--- "{item.track_title}"'), items='tracks'),
    Const("\n ОЖИДАЙТЕ ПРОВЕРКУ", when='on_process'),
    Const('Ваш трек находится на стадии отгрузки, ожидайте.', when='on_aggregate'),
    sep='\n'
)

create_new_release = Dialog(
    Window(
        # TODO сделать default в бд везде где надо выводить начальную информацию того или иного типа, например по дефолту ставить в заголовок релиза "Новый альбом"
        Const("Создайте или выберите работу"),
        ScrollingGroup(
            Select(
                Format("🎵 {item[1]}"),
                type_factory=int,
                id="ms",
                items="releases",
                item_id_getter=itemgetter(0),
                on_click=on_release
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
            hide_on_single_page=True
        ),
        Button(Const('❇️ Создать'), on_click=create_release, id='create_new_release'),
        BTN_CANCEL_BACK,
        getter=create_new_release_getter,
        state=ReleaseTrack.list
    )
)

lvl1_page = Dialog(
    Window(
        release_info,
        DynamicMedia('cover'),
        Group(
            Group(
                SwitchTo(Format('{text_title}'), id='create_release_title', state=ReleasePage1.title),
                SwitchTo(Format('{text_cover}'), id='create_release_cover', state=ReleasePage1.cover),
                Button(Format('{text_tracks}'), id='add_tracks_to_release', on_click=to_choose_tracks)
            ),
            Button(Const('Очистить треки'), on_click=clear_release_tracks, id='clear_tracks',
                   when=F['tracks'].len().is_not(0)),
            Button(Const('Отправить на проверку'), id='on_process_unsigned', on_click=on_approvement_lvl1,
                   when='all_done'),
            width=2,
            when='is_process'
        ),
        delete,
        BTN_CANCEL_BACK,
        state=ReleasePage1.main,
        getter=lvl1_getter
    ),
    Window(
        Const("Дайте название альбому"),
        DynamicMedia('cover'),
        MessageInput(set_release_title, content_types=[ContentType.TEXT]),
        MessageInput(release_title_oth),
        SwitchTo(TXT_BACK, 'from_title', ReleasePage1.main),
        state=ReleasePage1.title,
        getter=lvl1_getter
    ),
    Window(
        Format('{window_text}'),
        DynamicMedia('cover'),
        MessageInput(set_release_cover, content_types=[ContentType.DOCUMENT]),
        MessageInput(release_cover_oth),
        SwitchTo(TXT_BACK, 'from_cover', ReleasePage1.main),
        state=ReleasePage1.cover,
        getter=(cover_getter, lvl1_getter)
    )

)

choose_tracks = Dialog(
    Window(
        Const('Выберите треки, которые нужно добавить в альбом'),
        DynamicMedia('cover'),
        ScrollingGroup(
            Multiselect(
                Format('✓ {item[0]}'),
                Format('{item[0]}'),
                id='release_tracklist',
                items='items',
                item_id_getter=itemgetter(1),
            ),
            id='scroll_release',
            hide_on_single_page=True,
            width=1,
            height=4
        ),
        Button(Const('Готово'), on_click=all_tracks_selected, id='finish_select'),
        BTN_CANCEL_BACK,
        state=ReleaseTracks.start,
        getter=(choose_tracks_getter, lvl1_getter)
    )
)

lvl2_page = Dialog(
    Window(
        release_info,
        DynamicMedia('ld_file'),
        Group(
            SwitchTo(Format('{ld}'), 'users_ld', state=ReleasePage2.ld),
            Button(Const('Отправить на проверку'), id='on_process_signed', on_click=on_approvement_lvl2,
                   when='all_done'),
            when='is_process'
        ),
        delete,
        BTN_CANCEL_BACK,
        state=ReleasePage2.main,
        getter=lvl2_getter
    ),
    Window(
        Const("Прикрепите лицензионное соглашение в виде документа"),
        DynamicMedia('ld_file'),
        MessageInput(set_release_ld, content_types=[ContentType.DOCUMENT]),
        MessageInput(release_ld_oth),
        SwitchTo(TXT_BACK, 'from_ld', ReleasePage2.main),
        state=ReleasePage2.ld,
        getter=lvl2_getter
    )
)

lvl3_page = Dialog(
    Window(
        release_info,
        DynamicMedia('mail_photo'),
        Group(
            SwitchTo(Format('{mail}'), 'users_mail', state=ReleasePage3.mail),
            Button(Const('Отправить на проверку'), id='on_process_mail', on_click=on_approvement_lvl3, when='all_done'),
            when='is_process'
        ),
        delete,
        BTN_CANCEL_BACK,
        state=ReleasePage3.main,
        getter=lvl3_getter
    ),
    Window(
        Const("Прикрепите трек номер в виде фото (сжать изображение!)"),
        DynamicMedia('mail_photo'),
        MessageInput(set_release_mail, content_types=[ContentType.PHOTO]),
        MessageInput(release_mail_oth),
        SwitchTo(TXT_BACK, 'from_mail', ReleasePage3.main),
        state=ReleasePage3.mail,
        getter=lvl3_getter
    )
)
