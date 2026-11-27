from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from database import get_async_session
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse
from utils import calculate_urgency, determine_quadrant, calculate_days_until_deadline

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)


@router.get("", response_model=List[TaskResponse])
async def get_all_tasks(db: AsyncSession = Depends(get_async_session)) -> List[TaskResponse]:
    result = await db.execute(select(Task))
    return result.scalars().all()


@router.get("/quadrant/{quadrant}", response_model=List[TaskResponse])
async def get_tasks_by_quadrant(
    quadrant: str, db: AsyncSession = Depends(get_async_session)
) -> List[TaskResponse]:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4",
        )
    result = await db.execute(select(Task).where(Task.quadrant == quadrant))
    return result.scalars().all()


@router.get("/search", response_model=List[TaskResponse])
async def search_tasks(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_async_session),
) -> List[TaskResponse]:
    keyword = f"%{q}%"
    result = await db.execute(
        select(Task).where(
            (Task.title.ilike(keyword)) | (Task.description.ilike(keyword))
        )
    )
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(status_code=404, detail="По данному запросу ничего не найдено")
    return tasks


@router.get("/status/{status_value}", response_model=List[TaskResponse])
async def get_tasks_by_status(
    status_value: str, db: AsyncSession = Depends(get_async_session)
) -> List[TaskResponse]:
    if status_value not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="Недопустимый статус. Используйте: completed или pending",
        )
    is_completed = status_value == "completed"
    result = await db.execute(select(Task).where(Task.completed == is_completed))
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: int, db: AsyncSession = Depends(get_async_session)
) -> TaskResponse:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate, db: AsyncSession = Depends(get_async_session)
) -> TaskResponse:
    is_urgent = calculate_urgency(task.deadline_at)
    quadrant = determine_quadrant(task.is_important, is_urgent)

    new_task = Task(
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        is_urgent=is_urgent,
        quadrant=quadrant,
        deadline_at=task.deadline_at,
        completed=False,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> TaskResponse:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    if "is_important" in update_data or "deadline_at" in update_data:
        task.is_urgent = calculate_urgency(task.deadline_at)
        task.quadrant = determine_quadrant(task.is_important, task.is_urgent)

    if task_update.completed is True and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)
    elif task_update.completed is False:
        task.completed_at = None

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_async_session)) -> None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    await db.delete(task)
    await db.commit()
    return None