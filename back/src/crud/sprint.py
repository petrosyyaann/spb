from datetime import datetime
from typing import List

from core.db import Session
from sqlalchemy import select, and_
from models.sprint import Sprint


def get_sprint_by_id(sprint_id: int,
                     db: Session):
    pass


def get_all_sprints(from_date: datetime,
                    to_date: datetime,
                    db: Session) -> List[Sprint]:
    stmt = select(Sprint).where()
    stmt = stmt.where(and_(Sprint.sprint_start_date <= from_date,
                           Sprint.sprint_end_date >= to_date))
    res = db.execute(stmt)
    return res.scalars().all()
