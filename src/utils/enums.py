from enum import Enum


class State(Enum):
    PROCESS = 'process'
    REJECT = 'reject'
    APPROVE = 'approve'

    def __str__(self):
        return self.value


class Tables(Enum):
    USER = 'user'
    TRACK = 'track'
    RELEASE = 'release'
    EMPLOYEE = 'employee'
    TRACK_INFO = 'track_info'
    PERSONAL_DATA = 'personal_data'

    def __str__(self):
        return self.value


class Actions(Enum):
    PASS_DATA = 'all_passport_data'
    BANK_DATA = 'all_bank_data'
    RELEASE_UNSIGNED = 'unsigned_state'
    RELEASE_SIGNED = 'signed_state'
    RELEASE_MAIL = 'mail_track_state'
    TRACK_STATE = 'track_state'
    TRACK_INFO_STATE = 'info_state'

    def __str__(self):
        return self.value


class Privileges(Enum):
    MANAGER = 'manager'
    MODERATOR = 'moderator'
    CURATOR = 'curator'
    ADMIN = 'admin'

    def __str__(self):
        return self.value
