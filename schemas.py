from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название задачи")
    description: Optional[str] = Field(None, max_length=500, description="Описание задачи")
    is_important: bool = Field(..., description="Важность задачи")
    deadline_at: Optional[datetime] = Field(None, description="Плановый срок выполнения задачи")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_important: Optional[bool] = None
    deadline_at: Optional[datetime] = None
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    quadrant: str
    is_urgent: bool
    completed: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None
    user_id: Optional[int] = None
    days_until_deadline: Optional[int] = None
    status_message: Optional[str] = None

    class Config:
        from_attributes = True


class TimingStatsResponse(BaseModel):
    completed_on_time: int
    completed_late: int
    on_plan_pending: int
    overtime_pending: int