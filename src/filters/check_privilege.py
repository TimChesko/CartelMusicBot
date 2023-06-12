import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message


class CheckPrivilege(BaseFilter):
    available_privilege = ["user", "tester", "moderator", "admin"]

    def __init__(self, privilege):
        self.privilege = privilege

    async def __call__(self, obj: Message) -> bool:
        data = "admin"  # получить данные из бд
        if self.privilege in self.available_privilege and data in self.available_privilege:
            user_privilege_index = self.available_privilege.index(data)
            privilege_index = self.available_privilege.index(self.privilege)
            return user_privilege_index >= privilege_index
        logging.error(f"Не правильно прописанная привилегия: {self.privilege}")
        return False
