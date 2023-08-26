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
        self.set_logger_bind_and_msg()

    def set_logger_bind_and_msg(self):
        new_logger = self.logger
        patterns = [
            (r"^(.*?):\s*(.*)$", ["action", "details"]),
            (r"(.*)\((.*)\)", ["action", "details"]),
            (r"^(.*?) to id=(\d+) type='(.*?)' title=(.*?) username='(.*?)' first_name='(.*?)' last_name='(.*?)'",
             ["action", "user_id", "message_type", "title", "username", "first_name", "last_name"])
        ]
        for pattern, group_names in patterns:
            match = re.match(pattern, self.log_message)
            if match:
                groups = match.groups()
                data = {group_name: group for group_name, group in zip(group_names, groups)}
                action_message = data.pop('action', 'No action found')
                new_logger = new_logger.bind(_type="dialog", **data)
                new_logger.debug(action_message)
                break
        else:
            new_logger.error("Pattern not found for message:", self.log_message)


def setup_dialog_logging(dialog_logger):
    logging.root.handlers.clear()
    custom_handler = AiogramDialogLogging(dialog_logger, "aiogram_dialog")
    logging.root.addHandler(custom_handler)
