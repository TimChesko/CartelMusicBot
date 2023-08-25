from src.data.config import Config
from src.utils.enums import Privileges


def translate_privilege(privilege: Privileges) -> str:
    translations = {
        Privileges.MANAGER: "Менеджер",
        Privileges.MODERATOR: "Модератор",
        Privileges.CURATOR: "Куратор",
        Privileges.ADMIN: "Админ",
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
