from datetime import datetime
from fastapi import APIRouter, Depends
from models.user import User
from core.db import get_database, Session
from core.auth import get_user
from crud.sprint import get_all_sprints, get_sprint_by_id, get_sprints_with_ids, get_sprint_compare_to_all
from typing import List
from schemas.sprint import SprintBaseData, SprintResult, SprintCompareResult, SprintRecommendation
import core.errors as errors

router = APIRouter()


@router.get("/all",
            response_model=List[SprintBaseData],
            responses=errors.with_errors())
async def get_all_sprint_info(user: User = Depends(get_user),
                              db: Session = Depends(get_database)) -> List[SprintBaseData]:
    sprints = get_all_sprints(db)
    return [SprintBaseData(id=sprint.id,
                           name=sprint.name,
                           status=sprint.status,
                           to_date=sprint.to_date,
                           from_date=sprint.from_date,
                           tasks_in_sprint=sprint.tasks_in_sprint) for sprint in sprints]


"""
@router.get("/{sprint_id}/",
            response_model=List[SprintBaseData],
            responses=errors.with_errors())
async def get_useless_sprint_info(sprint_ids: List[int],
                                  user: User = Depends(get_user),
                                  db: Session = Depends(get_database)) -> List[SprintBaseData]:
    sprints = get_all_sprints(db)
    return [SprintBaseData(id=sprint.id,
                           name=sprint.name,
                           status=sprint.status,
                           to_date=sprint.to_date,
                           from_date=sprint.from_date,
                           tasks_in_sprint=sprint.tasks_in_sprint) for sprint in sprints]
"""


@router.post("/result",
             response_model=List[SprintResult])
async def get_sprint_result(sprint_ids: List[int],
                            user: User = Depends(get_user),
                            db: Session = Depends(get_database)) -> List[SprintResult]:
    sprints = get_sprints_with_ids(sprint_ids, db)
    return [SprintResult(sprint_id=sprint.id,
                         name=sprint.name,
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
                         tasks_in_sprint=sprint.tasks_in_sprint,
                         all_tasks_estimation=sprint.all_tasks_estimation,
                         recommendations=[SprintRecommendation(type=recommendation["type"],
                                                               text=recommendation["text"]) for recommendation in sprint.recommendations["data"]]) for sprint in sprints]


@router.get("/{sprint_id}/compare",
            response_model=SprintCompareResult)
async def compare_sprint_to_all(sprint_id: int,
                                user: User = Depends(get_user),
                                db: Session = Depends(get_database)) -> SprintCompareResult:
    sprint = get_sprint_by_id(sprint_id, db)
    if sprint is None:
        raise errors.sprint_not_found()
    sprint_analysis = get_sprint_compare_to_all(sprint.id, db)
    return SprintCompareResult(sprint_id=sprint.id,
                               to_do_estimation_points=sprint_analysis.to_do_estimation,
                               done_estimation_points=sprint_analysis.done_estimation,
                               processed_estimation_points=sprint_analysis.processed_estimation,
                               removed_estimation_points=sprint_analysis.removed_estimation,
                               blocked_tasks_points=sprint_analysis.blocked_tasks,
                               created_tasks_points=sprint_analysis.created_tasks,
                               excluded_tasks_points=sprint_analysis.excluded_tasks)

