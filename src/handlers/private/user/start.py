from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.FSM.fsm_user import AddNickname
from src.keyboards.start import markup_start
from src.models.user import UserHandler

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message, state: FSMContext, engine: AsyncEngine, database_logger: BoundLoggerFilteringAtDebug):
    user = await UserHandler(engine, database_logger).get_all_by_tg_id(msg.from_user.id)
    if not user:
        user = await UserHandler(engine, database_logger).add_new_user(msg)
        await msg.answer('Введите свой псевдоним:')
        await state.set_state(AddNickname.nickname)
    else:
        user = await UserHandler(engine, database_logger).get_user_nickname(msg.from_user.id)
        await msg.answer(f"{user} добро пожаловать в личный кабинет!", reply_markup=await markup_start())
    database_logger.debug(user)


@router.message(AddNickname.nickname, flags={'chat_action': 'typing'})
async def nickname_adding(msg: Message, state: FSMContext):
    await msg.answer(f"{msg.text} добро пожаловать в личный кабинет!", reply_markup=await markup_start())
    await state.clear()

