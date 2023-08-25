import logging
import re


class AiogramDialogLogging(logging.Handler):
    def __init__(self, logger, log_name):
        super().__init__()
        self.logger = logger
        self.log_name: str = log_name
        self.log_message = None

    def emit(self, record):
        self.log_message = self.format(record)
        msg = self.set_logger_bind_and_msg()
        self.logger.debug(msg)

    def set_logger_bind_and_msg(self):
        list_name = self.log_name.split(".")
        pattern = r"(\w+\s\w+|<\w+\s['\w:]+'>|\(\w+\s['\w:]+\))"
        bind_dict = {"type": "dialog"}
        match list_name:
            case _, "window":
                result = re.findall(pattern, self.log_message)
                msg = result[0]
                bind_dict.update({"window": result[1]})
            case _, "dialog":
                result = re.findall(pattern, self.log_message)
                msg = result[0]
                if len(result) == 3:
                    bind_dict.update({"state": result[1], "dialog_id": result[2]})
                elif len(result) == 2:
                    bind_dict.update({"dialog_id": result[1]})
            case _, "manager":
                pattern = r"(\w+)\s+to\s+id=(\d+)"
                matches = re.findall(pattern, self.log_message)
                results = [[action, id] for action, id in matches]
                msg = results[0][0]
                bind_dict.update({"user_id": results[0][1]})
            case _:
                msg = self.log_message
        self.logger.bind(**bind_dict)
        return msg


def setup_dialog_logging(dialog_logger):
    list_dialog_logs = [
        "aiogram_dialog.window",
        "aiogram_dialog.dialog",
        "aiogram_dialog.manager.message_manager"
    ]
    for log_name in list_dialog_logs:
        logger = logging.getLogger(log_name)
        custom_handler = AiogramDialogLogging(dialog_logger, log_name)
        logger.addHandler(custom_handler)
