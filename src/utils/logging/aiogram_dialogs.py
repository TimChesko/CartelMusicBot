import logging
import re


class AiogramDialogLogging(logging.Handler):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.log_message = None

    def emit(self, record):
        self.log_message = self.format(record)
        self.set_logger_bind_and_msg()

    def set_logger_bind_and_msg(self):
        new_logger = self.logger
        patterns = [
            (r"^(.*?):\s*(.*)$", ["action", "details"]),
            (r"(.*)\((.*)\)", ["action", "details"]),
            (r"(send_media to|remove_kbd in|edit_text to|send_text to) id=(\d+) type='(\w+)' "
             r"title=(\w+) username='(\w+)' first_name='(\w+)' last_name='(\w+)'",
             ["action", "user_id", "message_type", "title", "username", "first_name", "last_name"])
        ]
        if self.log_message in ["", "[]", "{}"]:
            return
        for pattern, group_names in patterns:
            match = re.match(pattern, self.log_message)
            if match:
                groups = match.groups()
                data = {group_name: group for group_name, group in zip(group_names, groups)}
                action_message = data.pop('action', 'No action found')
                new_logger = new_logger.bind(**data)
                new_logger.debug(action_message)
                break
        else:
            new_logger.error("Pattern not found for message: {}".format(self.log_message))


class AiogramDialogFilter(logging.Filter):
    def filter(self, record):
        path = record.name.split(".")
        return path[0] == "aiogram_dialog"


class AiogramFilter(logging.Filter):
    def filter(self, record):
        path = record.name.split(".")
        return path[0] == "aiogram"


def setup_dialog_logging(dialog_logger):
    logging.root.handlers.clear()

    dialog_handler = AiogramDialogLogging(dialog_logger)
    aiogram_dialog_filter = AiogramDialogFilter()

    dialog_handler.addFilter(aiogram_dialog_filter)
    logging.root.addHandler(dialog_handler)
