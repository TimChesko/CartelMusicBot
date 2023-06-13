from aiogram.fsm.state import StatesGroup, State


class AddNickname(StatesGroup):
    nickname = State()