from sqlalchemy import TIMESTAMP, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import List

from models.base import Base


class Sprint(Base):
    __tablename__ = "sprint"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str]
    sprint_start_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    sprint_end_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    entity_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer, dimensions=1),
                                                  server_default='{}')
