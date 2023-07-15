from aiogram.fsm.state import StatesGroup, State


class RegNickname(StatesGroup):
    nickname = State()
    finish = State()


class StartMenu(StatesGroup):
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


class MyTracksProcessed(StatesGroup):
    ...


class PersonalDataFilling(StatesGroup):
    start = State()
    info = State()
    firstname = State()
    surname = State()
    middlename = State()
    passport_series = State()  # серия паспорта
    passport_number = State()  # номер паспорта
    who_issued_it = State()  # кем выдан
    date_of_issue = State()  # когда выдан
    unit_code = State()  # код подразделения
    date_of_birth = State()  # дата рождения
    place_of_birth = State()  # место рождения
    registration_address = State()  # адрес регистрации
    physical_inn_code = State()  # ИНН по паспорту

    recipient = State()  # Получатель
    account_code = State()  # Номер счёта
    bik_code = State()  # БИК
    bank_recipient = State()  # Банк получатель
    correct_code = State()  # Корр. Счет
    inn_code = State()  # ИНН
    kpp_code = State()  # КПП
    swift_code = State()  # Свифт-код

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


class PersonalData(StatesGroup):
    confirm = State()


class ProfileEdit(StatesGroup):
    menu = State()
    process = State()


class DialogInput(StatesGroup):
    text = State()
    date = State()
