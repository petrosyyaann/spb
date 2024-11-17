from datetime import datetime
from typing import List
from dataclasses import dataclass
from core.db import Session
from sqlalchemy import select, text
from models.sprint import Sprint


@dataclass
class CompareSprint:
    to_do_estimation: float = 0.0
    done_estimation: float = 0.0
    processed_estimation: float = 0.0
    removed_estimation: float = 0.0
    blocked_tasks: float = 0.0
    created_tasks: float = 0.0
    excluded_tasks: float = 0.0


def get_sprint_by_id(sprint_id: int,
                     db: Session) -> Sprint | None:
    stmt = select(Sprint).where(Sprint.id == sprint_id)
    res = db.execute(stmt)
    return res.scalar_one_or_none()


def get_all_sprints(db: Session) -> List[Sprint]:
    stmt = select(Sprint).where()
    #stmt = stmt.where(and_(Sprint.sprint_start_date <= from_date,
    #                       Sprint.sprint_end_date >= to_date))
    res = db.execute(stmt)
    return res.scalars().all()


def get_sprints_with_ids(sprint_ids: List[int],
                         db: Session) -> List[Sprint]:
    stmt = select(Sprint).where(Sprint.id.in_(sprint_ids))
    res = db.execute(stmt)
    return res.scalars().all()


def get_sprint_compare_to_all(sprint_id: int,
                              db: Session) -> CompareSprint:
    res = db.execute(text("""
        WITH sprint_params AS (
        SELECT
            sprint.to_do_estimation AS to_do_estimation_1,
            sprint.done_estimation AS done_estimation_1,
            sprint.processed_estimation AS processed_estimation_1,
            sprint.removed_estimation AS removed_estimation_1,
            sprint.blocked_tasks AS blocked_tasks_1,
            sprint.created_tasks AS created_tasks_1,
            sprint.excluded_tasks AS excluded_tasks_1
        FROM sprint WHERE sprint.id = :sprint_id_1)
        SELECT
            COUNT(sprint.id) AS total_count,
            SUM(CASE WHEN sprint.to_do_estimation > sp.to_do_estimation_1 THEN 1 ELSE 0 END) AS to_do_estimation,
            SUM(CASE WHEN sprint.done_estimation > sp.done_estimation_1 THEN 1 ELSE 0 END) AS done_estimation,
            SUM(CASE WHEN sprint.processed_estimation > sp.processed_estimation_1 THEN 1 ELSE 0 END) AS processed_estimation,
            SUM(CASE WHEN sprint.removed_estimation > sp.removed_estimation_1 THEN 1 ELSE 0 END) AS removed_estimation,
            SUM(CASE WHEN sprint.blocked_tasks > sp.blocked_tasks_1 THEN 1 ELSE 0 END) AS blocked_tasks,
            SUM(CASE WHEN sprint.created_tasks > sp.created_tasks_1 THEN 1 ELSE 0 END) AS created_tasks,
            SUM(CASE WHEN sprint.excluded_tasks > sp.excluded_tasks_1 THEN 1 ELSE 0 END) AS excluded_tasks
        FROM sprint
        CROSS JOIN sprint_params sp;"""),
                     {"sprint_id_1": sprint_id})

    (all_sprints,
     to_do_estimation,
     done_estimation,
     processed_estimation,
     removed_estimation,
     blocked_tasks,
     created_tasks,
     excluded_tasks) = res.fetchall()[0]
    if all_sprints == 0:
        return CompareSprint()
    return CompareSprint(to_do_estimation=(all_sprints-to_do_estimation)/all_sprints,
                         done_estimation=(all_sprints-done_estimation)/all_sprints,
                         processed_estimation=(all_sprints-processed_estimation)/all_sprints,
                         removed_estimation=(all_sprints-removed_estimation)/all_sprints,
                         blocked_tasks=(all_sprints-blocked_tasks)/all_sprints,
                         created_tasks=(all_sprints-created_tasks)/all_sprints,
                         excluded_tasks=(all_sprints-excluded_tasks)/all_sprints)
