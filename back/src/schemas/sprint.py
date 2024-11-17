from typing import List

from pydantic import BaseModel, Field
from datetime import datetime


class SprintBaseData(BaseModel):
    id: int
    name: str
    status: str
    from_date: datetime
    to_date: datetime
    tasks_in_sprint: int


class SprintRecommendation(BaseModel):
    type: str
    text: str


class SprintResult(BaseModel):
    sprint_id: int
    from_date: datetime
    to_date: datetime
    backlog_update: float
    name: str
    to_do_estimation_points: List[float]
    done_estimation_points: List[float]
    processed_estimation_points: List[float]
    removed_estimation_points: List[float]
    blocked_tasks_points: List[float]
    created_tasks_points: List[float] = Field(description="Создано ч/д за определенный день в спринте")
    excluded_tasks_points: List[float] = Field(description="Удалено ч/д за определенный день в спринте")
    created_tasks_amount: List[int] = Field(description="Создано задач за определенный день в спринте")
    excluded_tasks_amount: List[int] = Field(description="Удалено задач за определенный день в спринте")
    all_tasks_estimation: float = Field(description="Сколько чд за весь спринт")
    tasks_in_sprint: int = Field(description="Сколько всего задач в спринте")
    recommendations: List[SprintRecommendation]


class SprintCompareResult(BaseModel):
    sprint_id: int
    to_do_estimation_points: float
    done_estimation_points: float
    processed_estimation_points: float
    removed_estimation_points: float
    blocked_tasks_points: float
    created_tasks_points: float
    excluded_tasks_points: float
