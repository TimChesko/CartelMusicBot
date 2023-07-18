from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from src.models.user import UserHandler


class CheckBan(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:
        if await UserHandler(data['session_maker'], data['database_logger']).get_ban_by_tg_id(event.from_user.id):
            return
        return await handler(event, data)
