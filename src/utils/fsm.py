from aiogram.fsm.state import StatesGroup, State


#  registrations states:
class RegNickname(StatesGroup):
    nickname = State()
    finish = State()


class StartMenu(StatesGroup):
    start = State()


# Listening states:
class Listening(StatesGroup):
    start = State()
    apply = State()
    finish = State()


# Listening
class Library(StatesGroup):
    start = State()
    process = State()
    reject = State()
    approve = State()
    public = State()


# License data states
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
    email = State()

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
