from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import MyTracks, MyTracksRejected, MyTracksApproved

my_tracks_menu = Dialog(
    Window(
        Const('Все Ваши работы в одном месте!'),
        Start(Const('🟢Одобренные🟢'), state=MyTracksApproved.start, id='my_tracks_approve'),
        # Start(Const('🟡В процессе🟡'), id='my_tracks_process'),
        Start(Const('🔴Отклоненные🔴'), state=MyTracksRejected.start, id='my_tracks_reject'),
        # Start(Const('Отгруженные'), id='my_tracks_aggregate'),
        Cancel(Const('Назад')),
        state=MyTracks.start
    ),
)
