from src.models.tables import Logs
from src.utils.enums import Tables, Actions, Status


def track_info_approve(employee_id, row_id):
    return Logs(employee_id=employee_id,
                table=Tables.TRACK_INFO,
                row_id=row_id,
                column_name=Actions.TRACK_INFO_STATE,
                action_type=Status.APPROVE)


def track_info_reject(employee_id, row_id, comment=None):
    return Logs(employee_id=employee_id,
                table=Tables.TRACK_INFO,
                row_id=row_id,
                column_name=Actions.TRACK_INFO_STATE,
                comment=comment,
                action_type=Status.APPROVE)
