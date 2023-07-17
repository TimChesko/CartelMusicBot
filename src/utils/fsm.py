from aiogram.fsm.state import StatesGroup, State


class RegNickname(StatesGroup):
    nickname = State()
    finish = State()


class RejectAnswer(StatesGroup):
    start = State()
    finish = State()


class StartMenu(StatesGroup):
    start = State()


class AdminMenu(StatesGroup):
    start = State()


class AdminListening(StatesGroup):
    start = State()


class AdminDashboardPIN(StatesGroup):
    start = State()


class AdminEmployee(StatesGroup):
    start = State()


class AdminStatistic(StatesGroup):
    start = State()


class AdminAddEmployee(StatesGroup):
    start = State()
    privilege = State()
    finish = State()


class AdminDashboard(StatesGroup):
    start = State()


class Listening(StatesGroup):
    start = State()
    track = State()
    apply = State()
    finish = State()


class ListeningNewTrack(StatesGroup):
    start = State()
    title = State()
    finish = State()


class ListeningEditTrack(StatesGroup):
    start = State()
    select_track = State()
    finish = State()


class MyTracks(StatesGroup):
    start = State()


class MyTracksApproved(StatesGroup):
    start = State()
    track_info = State()

    filling_data = State()

    confirm_title = State()
    update_title = State()

    get_text = State()

    set_beat_author = State()  # Автор бита (если сам артист переходит сразу в другой блок)
    purchased_beat = State()  # Купленный бит, нужно отчуждение
    percent_beat = State()  # Битмарь работает за процент, нужен процент битмаря

    set_text_author = State()  # Автор слов (если сам артист переходит сразу в другой блок)
    purchased_text = State()  # Купленные слова, нужно отчуждение
    percent_text = State()  # Автор слов работает под процент, нужен его процент

    explicit_content = State()  # Ненормативная лексика (да/нет)

    feat_or_not = State()  # Фит (да/нет)
    feat_percent = State()  # Процент от трека от заполняемой стороны (не от приглашаемого)
    invitation = State()  # Приглашение на фит (приглашаемый должен быть зареган в нашей системе)
    confirm_on_moderation = State()


class MyTracksRejected(StatesGroup):
    start = State()
    track_info = State()
    select_track = State()
    finish = State()


# Public tracks states
class PublicTrack(StatesGroup):
    list = State()


#  Service's states
class Service(StatesGroup):
    menu = State()


class Profile(StatesGroup):
    menu = State()


class Passport(StatesGroup):
    add_data = State()
    edit_data = State()

    confirm = State()


class Bank(StatesGroup):
    add_data = State()
    edit_data = State()

    confirm = State()


class Nickname(StatesGroup):
    edit = State()


class Social(StatesGroup):
    view_data = State()
    confirm = State()
    view_link = State()

class PersonalData(StatesGroup):
    confirm = State()


class ProfileEdit(StatesGroup):
    menu = State()
    process = State()


class DialogInput(StatesGroup):
    text = State()
    date = State()
