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
    track = State()
    text = State()
    title = State()
    apply = State()


class ListeningEditTrack(StatesGroup):
    select_track = State()


class Library(StatesGroup):
    start = State()
    process = State()
    reject = State()
    approve = State()
    public = State()


class MyData(StatesGroup):
    start = State()


class PublicTrack(StatesGroup):
    list = State()


class Service(StatesGroup):
    menu = State()
