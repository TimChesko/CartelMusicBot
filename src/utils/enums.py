from enum import Enum


class EnumBase(Enum):
    def __str__(self):
        return self.value


# TODO поправить в старте ссылку на фит
class FeatStatus(EnumBase):
    WAIT_FEAT = "WAIT_FEAT"
    WAIT_REG_FEAT = "WAIT_REG_FEAT"


class Status(EnumBase):
    PROCESS = 'PROCESS'
    REJECT = 'REJECT'
    APPROVE = 'APPROVE'


class Tables(EnumBase):
    USER = 'USER'
    TRACK = 'TRACK'
    RELEASE = 'RELEASE'
    EMPLOYEE = 'EMPLOYEE'
    TRACK_INFO = 'TRACK_INFO'
    PERSONAL_DATA = 'PERSONAL_DATA'


class Actions(EnumBase):
    PASS_DATA = 'ALL_PASSPORT_DATA'
    BANK_DATA = 'ALL_BANK_DATA'
    RELEASE_UNSIGNED = 'UNSIGNED_STATUS'
    RELEASE_SIGNED = 'SIGNED_STATUS'
    RELEASE_MAIL = 'MAIL_TRACK_STATUS'
    TRACK_STATE = 'TRACK_STATUS'
    TRACK_INFO_STATE = 'TRACK_INFO_STATUS'


class Privileges(EnumBase):
    MANAGER = 'MANAGER'
    MODERATOR = 'MODERATOR'
    CURATOR = 'CURATOR'
    ADMIN = 'ADMIN'


class EmployeeStatus(EnumBase):
    REGISTRATION = "REGISTRATION"  # the moderator has not registered yet
    WORKS = "WORKS"  # the moderator has been registered
    FIRED = "FIRED"  # the moderator has been fired (уволен)
