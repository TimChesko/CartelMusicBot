from src.models.tables import Logs
from src.utils.enums import Tables, Actions, Status


def unsigned_approve(employee_id, row_id):
    return Logs(employee_id=employee_id,
                table=Tables.RELEASE,
                row_id=row_id,
                column_name=Actions.RELEASE_UNSIGNED,
                action_type=Status.APPROVE)


def unsigned_reject(employee_id, row_id, comment=None):
    return Logs(employee_id=employee_id,
                table=Tables.RELEASE,
                row_id=row_id,
                column_name=Actions.RELEASE_UNSIGNED,
                comment=comment,
                action_type=Status.REJECT)


def signed_approve(employee_id, row_id):
    return Logs(employee_id=employee_id,
                table=Tables.RELEASE,
                row_id=row_id,
                column_name=Actions.RELEASE_SIGNED,
                action_type=Status.APPROVE)


def signed_reject(employee_id, row_id, comment=None):
    return Logs(employee_id=employee_id,
                table=Tables.RELEASE,
                row_id=row_id,
                column_name=Actions.RELEASE_SIGNED,
                comment=comment,
                action_type=Status.REJECT)


def mail_approve(employee_id, row_id):
    return Logs(employee_id=employee_id,
                table=Tables.RELEASE,
                row_id=row_id,
                column_name=Actions.RELEASE_MAIL,
                action_type=Status.APPROVE)


def mail_reject(employee_id, row_id, comment=None):
    return Logs(employee_id=employee_id,
                table=Tables.RELEASE,
                row_id=row_id,
                column_name=Actions.RELEASE_MAIL,
                comment=comment,
                action_type=Status.REJECT)
