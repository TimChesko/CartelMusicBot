from aiogram import Router
from aiogram.types import Message
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.middlewares.check_privilege import CheckPrivilege
from src.models.user import UserHandler

router = Router()


# @router.message(lambda c: c.text.startswith("/privilege"))
# async def privilege(msg: Message, config, engine, database_logger: BoundLoggerFilteringAtDebug):
#     command = msg.text.split(" ")
#     match command:
#         case _, "list":
#             privilege_list = list(map(lambda c: f"\n{c}", config.PRIVILEGES))
#             privilege_text = ''.join(privilege_list)
#             await msg.answer(f'Список привилегий:\n{privilege_text}')
#         case _, "set":
#             await msg.answer("Вы забыли 2 аргумента: id пользователя, привелегия\n"
#                              "Пример: /privilege set 123123 moderator")
#         case _, "set", str(tg_id_str), str(privilege_str):
#             try:
#                 tg_id = int(tg_id_str)
#                 if tg_id != msg.from_user.id:
#                     if await CheckPrivilege(privilege_str).simple(engine, database_logger, msg, config):
#                         await UserHandler(engine, database_logger).set_privilege(tg_id, privilege_str)
#                         await msg.answer(f"Привилегия {privilege_str} присвоена пользователю {tg_id}")
#                     else:
#                         await msg.answer("Данной привилегии не существует или "
#                                          "ваша привилегии ниже привилегии которую вы хотите присвоить")
#                 else:
#                     await msg.answer(f"В целях безопасности, вы не можете изменить свою роль")
#             except ValueError:
#                 await msg.answer("Пришлите id в виде числа")
#         case _, "del":
#             await msg.answer("Вы забыли 1 аргумент: id пользователя\n"
#                              "Пример: /privilege del 123123")
#         case _, "del", str(tg_id_str):
#             try:
#                 tg_id = int(tg_id_str)
#                 if tg_id != msg.from_user.id:
#                     await UserHandler(engine, database_logger).set_privilege(tg_id, 'user')
#                     await msg.answer(f"У пользователя {tg_id} сброшена привелегия до 'user' ")
#                 else:
#                     await msg.answer(f"В целях безопасности, вы не можете изменить свою роль")
#             except ValueError:
#                 await msg.answer("Пришлите id в виде числа")
#         case _:
#             await msg.answer("Доступные команды:\n\n"
#                              "/privilege list - список команд\n"
#                              "/privilege set {id} {privilege} - присвоить привилегию пользователю\n"
#                              "/privilege del {id} - отобрать привилегию у пользователя\n")
