from src.data import config


def translate_privilege(privilege: str) -> str:
    translations = {
        "user": "Юзер",
        "tester": "Тестер",
        "manager": "Менеджер",
        "moderator": "Модератор",
        "curator": "Куратор",
        "admin": "Админ",
    }
    return translations[privilege]


def privilege_level(privilege: str | None) -> dict:
    """
    :param privilege: privilege from DB, for privilege levels list check .env PRIVILEGES
    None - developer access
    :return: dict for aiogram_dialog's Window getter, when=privilege level you need
    """
    if privilege is None:
        return {
            privilege: True for privilege in config.PRIVILEGES
        }
    user_privilege_index = config.PRIVILEGES.index(privilege)
    return {
        privilege: user_privilege_index >= config.PRIVILEGES.index(privilege) for privilege in config.PRIVILEGES
    }
