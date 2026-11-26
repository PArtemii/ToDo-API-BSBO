from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import Optional
from database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_important = Column(Boolean, nullable=False, default=False)
    is_urgent = Column(Boolean, nullable=False, default=False)
    quadrant = Column(String(2), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', quadrant='{self.quadrant}')>"

    def days_until_deadline(self) -> Optional[int]:
        if self.deadline is None:
            return None
        return (self.deadline.date() - datetime.now(timezone.utc).date()).days

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_important": self.is_important,
            "is_urgent": self.is_urgent,
            "quadrant": self.quadrant,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "deadline": self.deadline,
            "days_until_deadline": self.days_until_deadline(),
        }