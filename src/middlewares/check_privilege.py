from typing import Any, Awaitable, Callable, Dict

from aiogram.types import TelegramObject, Message

from src.data import config
from src.models.user import UserHandler


class CheckPrivilege:
    available_privilege = ["user", "tester", "moderator", "admin"]

    def __init__(self, privilege):
        self.privilege = privilege

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:

        info = await UserHandler(data['engine'], data['database_logger']).get_privilege_by_tg_id(event.from_user.id)

        if event.from_user.id in config.DEVELOPERS:
            return await handler(event, data)
        elif self.privilege in self.available_privilege and info in self.available_privilege:
            user_privilege_index = self.available_privilege.index(info)
            privilege_index = self.available_privilege.index(self.privilege)
            if user_privilege_index >= privilege_index:
                return await handler(event, data)
        return
