from src.models.tables import LogsEmployee
from src.utils.enums import Tables, Actions, Status


class LogEmp:

    def __init__(self, employee_id: int, row_id: int):
        self.employee_id = employee_id
        self.row_id = row_id

    def track_approve(self):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.TRACK,
                            row_id=self.row_id,
                            column_name=Actions.TRACK_STATE,
                            action_type=Status.APPROVE)

    def track_reject(self, comment=None):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.TRACK,
                            row_id=self.row_id,
                            column_name=Actions.TRACK_STATE,
                            comment=comment,
                            action_type=Status.REJECT)

    def passport_approve(self, ):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.PERSONAL_DATA,
                            row_id=self.row_id,
                            column_name=Actions.PASS_DATA,
                            action_type=Status.APPROVE)

    def passport_reject(self, comment=None):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.PERSONAL_DATA,
                            row_id=self.row_id,
                            column_name=Actions.PASS_DATA,
                            comment=comment,
                            action_type=Status.REJECT)

    def bank_approve(self, ):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.PERSONAL_DATA,
                            row_id=self.row_id,
                            column_name=Actions.BANK_DATA,
                            action_type=Status.APPROVE)

    def bank_reject(self, comment=None):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.PERSONAL_DATA,
                            row_id=self.row_id,
                            column_name=Actions.BANK_DATA,
                            comment=comment,
                            action_type=Status.REJECT)

    def unsigned_approve(self, ):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.RELEASE,
                            row_id=self.row_id,
                            column_name=Actions.RELEASE_UNSIGNED,
                            action_type=Status.APPROVE)

    def unsigned_reject(self, comment=None):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.RELEASE,
                            row_id=self.row_id,
                            column_name=Actions.RELEASE_UNSIGNED,
                            comment=comment,
                            action_type=Status.REJECT)

    def signed_approve(self, ):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.RELEASE,
                            row_id=self.row_id,
                            column_name=Actions.RELEASE_SIGNED,
                            action_type=Status.APPROVE)

    def signed_reject(self, comment=None):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.RELEASE,
                            row_id=self.row_id,
                            column_name=Actions.RELEASE_SIGNED,
                            comment=comment,
                            action_type=Status.REJECT)

    def mail_approve(self, ):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.RELEASE,
                            row_id=self.row_id,
                            column_name=Actions.RELEASE_MAIL,
                            action_type=Status.APPROVE)

    def mail_reject(self, comment=None):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.RELEASE,
                            row_id=self.row_id,
                            column_name=Actions.RELEASE_MAIL,
                            comment=comment,
                            action_type=Status.REJECT)

    def track_info_approve(self):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.TRACK_INFO,
                            row_id=self.row_id,
                            column_name=Actions.TRACK_INFO_STATE,
                            action_type=Status.APPROVE)

    def track_info_reject(self, comment=None):
        return LogsEmployee(employee_id=self.employee_id,
                            table=Tables.TRACK_INFO,
                            row_id=self.row_id,
                            column_name=Actions.TRACK_INFO_STATE,
                            comment=comment,
                            action_type=Status.APPROVE)
