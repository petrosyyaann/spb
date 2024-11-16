from datetime import datetime
from fastapi import APIRouter, Depends
from models.user import User
from core.db import get_database, Session
from core.auth import get_user
from crud.sprint import get_all_sprints
from typing import List
from schemas.sprint import SprintBaseData
import core.errors as errors


router = APIRouter()


@router.get("/all",
            responses=errors.with_errors())
async def get_sprint_info(user: User = Depends(get_user),
                          db: Session = Depends(get_database)):
    pass


@router.get("/{sprint_id}/",
            response_model=List[SprintBaseData],
            responses=errors.with_errors())
async def get_all_sprint_info(from_date: datetime,
                              to_date: datetime,
                              user: User = Depends(get_user),
                              db: Session = Depends(get_database)):
    sprints = get_all_sprints(from_date, to_date, db)
    return [SprintBaseData(id=sprint.id,
                           name=sprint.name,
                           status=sprint.status,
                           to_date=sprint.sprint_end_date,
                           from_date=sprint.sprint_start_date,
                           tasks_in_sprint=len(sprint.entity_ids)) for sprint in sprints]
