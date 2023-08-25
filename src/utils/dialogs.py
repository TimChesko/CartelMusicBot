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
        self.logger.debug(self.log_message)
        self.set_logger_bind()

    def set_logger_bind(self):
        list_name = self.log_name.split(".")
        pattern = r"(\w+\s\w+|<\w+\s['\w:]+'>|\(\w+\s['\w:]+\))"
        bind_dict = {"type": "dialog"}
        msg = ""
        match list_name:
            case _, "window":
                pass
            case _, "dialog":
                result = re.findall(pattern, self.log_message)
                msg = result[0]
                bind_dict.update({"state": result[1], "dialog_id": result[2]})
            case _, "manager":
                pass
            case _:
                pass

        self.logger.bind(**bind_dict)

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
