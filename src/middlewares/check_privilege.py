from typing import Any, Awaitable, Callable, Dict

from aiogram.types import TelegramObject, Message

from src.data import config
from src.models.user import UserHandler


class CheckPrivilege:

    def __init__(self, privilege):
        self.privilege = privilege

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:

        info = await UserHandler(data['engine'], data['database_logger']).get_privilege_by_tg_id(event.from_user.id)

        if event.from_user.id in data['config'].DEVELOPERS:
            return await handler(event, data)
        elif self.privilege in data['config'].PRIVILEGES and info in data['config'].PRIVILEGES:
            user_privilege_index = data['config'].PRIVILEGES.index(info)
            privilege_index = data['config'].PRIVILEGES.index(self.privilege)
            if user_privilege_index >= privilege_index:
                return await handler(event, data)
        return

    async def simple(self, engine, logger, msg, cfg) -> bool:
        info = await UserHandler(engine, logger).get_privilege_by_tg_id(msg.from_user.id)

        if msg.from_user.id in cfg.DEVELOPERS:
            return True
        elif self.privilege in cfg.PRIVILEGES and info in cfg.PRIVILEGES:
            user_privilege_index = cfg.PRIVILEGES.index(info)
            privilege_index = cfg.PRIVILEGES.index(self.privilege)
            if user_privilege_index >= privilege_index:
                return True
        return False
