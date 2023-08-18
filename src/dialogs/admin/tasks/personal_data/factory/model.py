import dataclasses


@dataclasses.dataclass
class Task:
    column_id: int
    column_name: str
    title: str
    value: str
