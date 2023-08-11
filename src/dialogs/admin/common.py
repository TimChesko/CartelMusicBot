from src.data.config import Config


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
            privilege: True for privilege in Config.constant.privileges
        }
    user_privilege_index = Config.constant.privileges.index(privilege)
    return {
        privilege: user_privilege_index >= Config.constant.privileges.index(privilege) for privilege in
        Config.constant.privileges
    }
