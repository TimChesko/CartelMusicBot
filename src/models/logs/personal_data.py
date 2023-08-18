from src.models.tables import Logs
from src.utils.enums import Tables, Actions, Status


def passport_approve(employee_id, row_id):
    return Logs(employee_id=employee_id,
                table=Tables.PERSONAL_DATA,
                row_id=row_id,
                column_name=Actions.PASS_DATA,
                action_type=Status.APPROVE)


def passport_reject(employee_id, row_id, comment=None):
    return Logs(employee_id=employee_id,
                table=Tables.PERSONAL_DATA,
                row_id=row_id,
                column_name=Actions.PASS_DATA,
                comment=comment,
                action_type=Status.REJECT)


def bank_approve(employee_id, row_id):
    return Logs(employee_id=employee_id,
                table=Tables.PERSONAL_DATA,
                row_id=row_id,
                column_name=Actions.BANK_DATA,
                action_type=Status.APPROVE)


def bank_reject(employee_id, row_id, comment=None):
    return Logs(employee_id=employee_id,
                table=Tables.PERSONAL_DATA,
                row_id=row_id,
                column_name=Actions.BANK_DATA,
                comment=comment,
                action_type=Status.REJECT)
