from aiogram_dialog import StartMode

from src.models.tables import User
from src.utils.fsm import RegNickname


async def check_user(user: User, user_handler, dialog_manager, msg) -> bool:
    if not user:
        await user_handler.add_new_user(msg)
        user = await user_handler.get_user_by_tg_id(msg.from_user.id)
    await msg.delete()
    if user.nickname is None:
        await dialog_manager.start(RegNickname.nickname, mode=StartMode.RESET_STACK)
    elif user and user.nickname is not None:
        return True
    else:
        return False
