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

            (r"^(.*?) to id=(\d+) type='(\w+)' title=(\w+) username='(\w+)' first_name='(\w+)' last_name='(\w+)' "
             r"is_forum=(\w+) photo=(\w+) active_usernames=(\w+) emoji_status_custom_emoji_id=(\w+) bio=(\w+) "
             r"has_private_forwards=(\w+) has_restricted_voice_and_video_messages=(\w+) join_to_send_messages=(\w+) "
             r"join_by_request=(\w+) description=(\w+) invite_link=(\w+) pinned_message=(\w+) permissions=(\w+) "
             r"slow_mode_delay=(\w+) message_auto_delete_time=(\w+) has_aggressive_anti_spam_enabled=(\w+) "
             r"has_hidden_members=(\w+) has_protected_content=(\w+) sticker_set_name=(\w+) "
             r"can_set_sticker_set=(\w+) "
             r"linked_chat_id=(\w+) location=(\w+)$",
             ["action", "user_id", "message_type", "title", "username", "first_name", "last_name", "is_forum",
              "photo", "active_usernames", "emoji_status_custom_emoji_id", "bio", "has_private_forwards",
              "has_restricted_voice_and_video_messages", "join_to_send_messages", "join_by_request", "description",
              "invite_link", "pinned_message", "permissions", "slow_mode_delay", "message_auto_delete_time",
              "has_aggressive_anti_spam_enabled", "has_hidden_members", "has_protected_content", "sticker_set_name",
              "can_set_sticker_set", "linked_chat_id", "location"]),

            (r"^(\w+) in id=(\d+) type='(\w+)' title=(\w+) username='(\w+)' first_name='(\w+)' last_name='(\w+)' "
             r"is_forum=(\w+) photo=(\w+) active_usernames=(\w+) emoji_status_custom_emoji_id=(\w+) bio=(\w+) "
             r"has_private_forwards=(\w+) has_restricted_voice_and_video_messages=(\w+) join_to_send_messages=(\w+) "
             r"join_by_request=(\w+) description=(\w+) invite_link=(\w+) pinned_message=(\w+) permissions=(\w+) "
             r"slow_mode_delay=(\w+) message_auto_delete_time=(\w+) has_aggressive_anti_spam_enabled=(\w+) "
             r"has_hidden_members=(\w+) has_protected_content=(\w+) sticker_set_name=(\w+) "
             r"can_set_sticker_set=(\w+) "
             r"linked_chat_id=(\w+) location=(\w+)$",
             ["action", "user_id", "message_type", "title", "username", "first_name", "last_name", "is_forum",
              "photo", "active_usernames", "emoji_status_custom_emoji_id", "bio", "has_private_forwards",
              "has_restricted_voice_and_video_messages", "join_to_send_messages", "join_by_request", "description",
              "invite_link", "pinned_message", "permissions", "slow_mode_delay", "message_auto_delete_time",
              "has_aggressive_anti_spam_enabled", "has_hidden_members", "has_protected_content", "sticker_set_name",
              "can_set_sticker_set", "linked_chat_id", "location"])
        ]
        if self.log_message in ["", "[]", "{}"]:
            return
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
            new_logger.error("Pattern not found for message: {}".format(self.log_message))


def setup_dialog_logging(dialog_logger):
    logging.root.handlers.clear()
    custom_handler = AiogramDialogLogging(dialog_logger, "aiogram_dialog")
    logging.root.addHandler(custom_handler)
