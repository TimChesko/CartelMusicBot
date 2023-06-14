from aiogram.fsm.state import StatesGroup, State


class DialogRegNickname(StatesGroup):
    nickname = State()
    finish = State()
