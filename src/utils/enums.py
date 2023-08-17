from enum import Enum


class FeatStatus(Enum):
    WAIT_FEAT = "WAIT_FEAT"
    WAIT_REG_FEAT = "WAIT_REG_FEAT"


class Status(Enum):
    PROCESS = 'PROCESS'
    REJECT = 'REJECT'
    APPROVE = 'APPROVE'


class Tables(Enum):
    USER = 'user'
    TRACK = 'track'
    RELEASE = 'release'
    EMPLOYEE = 'employee'
    TRACK_INFO = 'track_info'
    PERSONAL_DATA = 'personal_data'


class Actions(Enum):
    PASS_DATA = 'all_passport_data'
    BANK_DATA = 'all_bank_data'
    RELEASE_UNSIGNED = 'unsigned_state'
    RELEASE_SIGNED = 'signed_state'
    RELEASE_MAIL = 'mail_track_state'
    TRACK_STATE = 'track_state'
    TRACK_INFO_STATE = 'info_state'


class Privileges(Enum):
    MANAGER = 'MANAGER'
    MODERATOR = 'MODERATOR'
    CURATOR = 'CURATOR'
    ADMIN = 'ADMIN'


class EmployeeStatus(Enum):
    REGISTRATION = "REGISTRATION"  # the moderator has not registered yet
    WORKS = "WORKS"  # the moderator has been registered
    FIRED = "FIRED"  # the moderator has been fired (уволен)
