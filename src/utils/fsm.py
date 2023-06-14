from aiogram.fsm.state import StatesGroup, State


class RegNickname(StatesGroup):
    nickname = State()
    finish = State()


class StartMenu(StatesGroup):
    start = State()


class Listening(StatesGroup):
    start = State()
    music_file = State()
    finish = State()


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
