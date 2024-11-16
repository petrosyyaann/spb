from pydantic import BaseModel
from datetime import datetime


class SprintBaseData(BaseModel):
    id: int
    name: str
    status: str
    from_date: datetime
    to_date: datetime
    tasks_in_sprint: int
