from sqlalchemy import TIMESTAMP, ARRAY, Integer, FLOAT
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import List, Dict, Any

from models.base import Base


class Sprint(Base):
    __tablename__ = "sprint"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str]
    from_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    to_date:  Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    backlog_update: Mapped[float] = mapped_column(nullable=False)

    to_do_estimation_points: Mapped[List[float]] = mapped_column(ARRAY(FLOAT, dimensions=1),
                                                                 server_default='{}')
    done_estimation_points: Mapped[List[float]] = mapped_column(ARRAY(FLOAT, dimensions=1),
                                                                server_default='{}')
    processed_estimation_points: Mapped[List[float]] = mapped_column(ARRAY(FLOAT, dimensions=1),
                                                                     server_default='{}')
    removed_estimation_points: Mapped[List[float]] = mapped_column(ARRAY(FLOAT, dimensions=1),
                                                                   server_default='{}')
    blocked_tasks_points: Mapped[List[float]] = mapped_column(ARRAY(FLOAT, dimensions=1),
                                                              server_default='{}')
    created_tasks_points: Mapped[List[float]] = mapped_column(ARRAY(FLOAT, dimensions=1),
                                                              server_default='{}')
    excluded_tasks_points: Mapped[List[float]] = mapped_column(ARRAY(FLOAT, dimensions=1),
                                                               server_default='{}')
    created_tasks_amount: Mapped[List[int]] = mapped_column(ARRAY(Integer, dimensions=1),
                                                            server_default='{}')
    excluded_tasks_amount: Mapped[List[int]] = mapped_column(ARRAY(Integer, dimensions=1),
                                                             server_default='{}')

    tasks_in_sprint: Mapped[int] = mapped_column(nullable=False)
    to_do_estimation: Mapped[float] = mapped_column(server_default='0.0')
    done_estimation: Mapped[float] = mapped_column(server_default='0.0')
    processed_estimation: Mapped[float] = mapped_column(server_default='0.0')
    removed_estimation: Mapped[float] = mapped_column(server_default='0.0')
    blocked_tasks: Mapped[float] = mapped_column(server_default='0.0')
    created_tasks: Mapped[float] = mapped_column(server_default='0.0')
    excluded_tasks: Mapped[float] = mapped_column(server_default='0.0')
    all_tasks_estimation: Mapped[float] = mapped_column(server_default='0.0')
    recommendations: Mapped[Dict[Any, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
