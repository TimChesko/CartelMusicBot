import logging

from src.data.config import Config


def translate_privilege(privilege: str) -> str:
    translations = {
        "user": "Юзер",
        "tester": "Тестер",
        "MANAGER": "Менеджер",
        "MODERATOR": "Модератор",
        "CURATOR": "Куратор",
        "ADMIN": "Админ",
    }
    return translations[privilege]


def privilege_level(config: Config, privilege: str | None) -> dict:
    if privilege == 'developer':
        return {
            privilege: True for privilege in config.constant.privileges
        }
    elif privilege is None:
        return {
            privilege: False for privilege in config.constant.privileges
        }
    user_privilege_index = config.constant.privileges.index(privilege)
    return {
        privilege: user_privilege_index >= config.constant.privileges.index(privilege) for privilege in
        config.constant.privileges
    }
