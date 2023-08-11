from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.data.config import load_config
from src.models.employee import EmployeeHandler


class EmployeeCheck(BaseFilter):

    async def __call__(self,
                       message: Message,
                       session_maker: async_sessionmaker,
                       database_logger: BoundLoggerFilteringAtDebug) -> Any:
        config = load_config()
        privilege = await (EmployeeHandler(session_maker, database_logger)
                           .check_employee_by_tg_id(message.from_user.id))
        return privilege or message.from_user.id in config.constant.developers
