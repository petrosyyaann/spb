from datetime import datetime
from fastapi import APIRouter, Depends
from models.user import User
from core.db import get_database, Session
from core.auth import get_user
from crud.sprint import get_all_sprints, get_sprint_by_id
from typing import List
from schemas.sprint import SprintBaseData, SprintResult
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
                              db: Session = Depends(get_database)) -> List[SprintBaseData]:
    sprints = get_all_sprints(from_date, to_date, db)
    return [SprintBaseData(id=sprint.id,
                           name=sprint.name,
                           status=sprint.status,
                           to_date=sprint.to_date,
                           from_date=sprint.from_date,
                           tasks_in_sprint=sprint.tasks_in_sprint) for sprint in sprints]


@router.get("/{sprint_id}/result",
            response_model=SprintResult)
async def get_sprint_result(sprint_id: int,
                            user: User = Depends(get_user),
                            db: Session = Depends(get_database)) -> SprintResult:
    sprint = get_sprint_by_id(sprint_id, db)
    return SprintResult(sprint_id=sprint.id,
                        from_date=sprint.from_date,
                        to_date=sprint.to_date,
                        backlog_update=sprint.backlog_update,
                        to_do_estimation_points=sprint.to_do_estimation_points,
                        done_estimation_points=sprint.done_estimation_points,
                        processed_estimation_points=sprint.processed_estimation_points,
                        removed_estimation_points=sprint.removed_estimation_points,
                        blocked_tasks_points=sprint.blocked_tasks_points,
                        created_tasks_points=sprint.created_tasks_points,
                        excluded_tasks_points=sprint.excluded_tasks_points,
                        created_tasks_amount=sprint.created_tasks_amount,
                        excluded_tasks_amount=sprint.excluded_tasks_amount,
                        tasks_in_sprint=sprint.tasks_in_sprint)
