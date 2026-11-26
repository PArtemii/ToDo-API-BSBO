from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Task as TaskModel
from schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)


def get_quadrant(is_important: bool, is_urgent: bool) -> str:
    if is_important and is_urgent:
        return "Q1"
    if is_important and not is_urgent:
        return "Q2"
    if not is_important and is_urgent:
        return "Q3"
    return "Q4"


@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()


@router.get("/search", response_model=List[TaskResponse])
async def search_tasks(
    q: str = Query(..., min_length=2, description="Ключевое слово для поиска"),
    db: Session = Depends(get_db),
):
    pattern = f"%{q}%"
    results = (
        db.query(TaskModel)
        .filter(
            (TaskModel.title.ilike(pattern))
            | (TaskModel.description.ilike(pattern))
        )
        .all()
    )
    if not results:
        raise HTTPException(status_code=404, detail="Задачи не найдены")
    return results


@router.get("/status/{status_value}", response_model=List[TaskResponse])
async def get_tasks_by_status(status_value: str, db: Session = Depends(get_db)):
    if status_value not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="Статус не найден. Используйте: completed или pending",
        )
    completed_flag = status_value == "completed"
    return db.query(TaskModel).filter(TaskModel.completed == completed_flag).all()


@router.get("/quadrant/{quadrant}", response_model=List[TaskResponse])
async def get_tasks_by_quadrant(quadrant: str, db: Session = Depends(get_db)):
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4",
        )
    return db.query(TaskModel).filter(TaskModel.quadrant == quadrant).all()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        is_urgent=task.is_urgent,
        quadrant=get_quadrant(task.is_important, task.is_urgent),
        completed=False,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, task: TaskUpdate, db: Session = Depends(get_db)
):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    update_data = task.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db_task.quadrant = get_quadrant(db_task.is_important, db_task.is_urgent)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(db_task)
    db.commit()
    return None