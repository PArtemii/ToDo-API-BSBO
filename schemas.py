from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime
from utils import calculate_days_until_deadline, calculate_urgency


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название задачи")
    description: Optional[str] = Field(None, max_length=500, description="Описание задачи")
    is_important: bool = Field(..., description="Важность задачи")
    deadline_at: Optional[datetime] = Field(None, description="Плановый срок выполнения задачи")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Новое название задачи")
    description: Optional[str] = Field(None, max_length=500, description="Новое описание")
    is_important: Optional[bool] = Field(None, description="Новая важность")
    deadline_at: Optional[datetime] = Field(None, description="Новый дедлайн")
    completed: Optional[bool] = Field(None, description="Статус выполнения")


class TaskResponse(TaskBase):
    id: int = Field(..., description="Уникальный идентификатор задачи", examples=[1])
    quadrant: str = Field(..., description="Квадрант матрицы Эйзенхауэра (Q1, Q2, Q3, Q4)", examples=["Q1"])
    is_urgent: bool = Field(..., description="Срочность задачи (вычисляется автоматически)")
    completed: bool = Field(default=False, description="Статус выполнения задачи")
    created_at: datetime = Field(..., description="Дата и время создания задачи")
    completed_at: Optional[datetime] = Field(None, description="Дата и время завершения задачи")

    # Делаем поля вычисляемыми автоматически на основе deadline_at
    @computed_field
    @property
    def days_until_deadline(self) -> Optional[int]:
        if self.deadline_at is None:
            return None
        return calculate_days_until_deadline(self.deadline_at)

    @computed_field
    @property
    def status_message(self) -> str:
        days = self.days_until_deadline
        if days is not None and days < 0 and not self.completed:
            return "Задача просрочена"
        return "Всё по плану"

    class Config:
        from_attributes = True


class TimingStatsResponse(BaseModel):
    completed_on_time: int = Field(..., description="Количество задач, завершенных в срок")
    completed_late: int = Field(..., description="Количество задач, завершенных с нарушением сроков")
    on_plan_pending: int = Field(..., description="Количество задач в работе, выполняемых в соответствии с планом")
    overtime_pending: int = Field(..., description="Количество просроченных незавершенных задач")