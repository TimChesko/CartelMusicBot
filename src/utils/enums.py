from enum import Enum


class EnumBase(Enum):
    def __str__(self):
        return self.value


class FeatStatus(EnumBase):
    WAIT_FEAT = "wait_feat"
    WAIT_REG_FEAT = "wait_reg_feat"


class Status(EnumBase):
    PROCESS = 'process'
    REJECT = 'reject'
    APPROVE = 'approve'


class Tables(EnumBase):
    USER = 'user'
    TRACK = 'track'
    RELEASE = 'release'
    EMPLOYEE = 'employee'
    TRACK_INFO = 'track_info'
    PERSONAL_DATA = 'personal_data'


class Actions(EnumBase):
    PASS_DATA = 'all_passport_data'
    BANK_DATA = 'all_bank_data'
    RELEASE_UNSIGNED = 'unsigned_state'
    RELEASE_SIGNED = 'signed_state'
    RELEASE_MAIL = 'mail_track_state'
    TRACK_STATE = 'track_state'
    TRACK_INFO_STATE = 'info_state'


class Privileges(EnumBase):
    MANAGER = 'manager'
    MODERATOR = 'moderator'
    CURATOR = 'curator'
    ADMIN = 'admin'


class EmployeeStatus(EnumBase):
    REGISTRATION = "registration"  # the moderator has not registered yet
    WORKS = "works"  # the moderator has been registered
    FIRED = "fired"  # the moderator has been fired (уволен)
