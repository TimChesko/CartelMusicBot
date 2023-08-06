from typing import Any, Awaitable, Callable, Dict

from aiogram.types import TelegramObject, Message

from src.data import config
from src.models.employee import EmployeeHandler


class EmployeeCheck:

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:
        privilege = await (EmployeeHandler(data['session_maker'], data['database_logger'])
                           .check_employee_by_tg_id(event.from_user.id))
        if privilege or event.from_user.id in config.DEVELOPERS:
            return await handler(event, data)
        return


