from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Task as TaskModel

router = APIRouter(
    prefix="/tasks",
    tags=["stats"],
)


@router.get("/stats")
async def get_tasks_stats(db: Session = Depends(get_db)) -> dict:
    tasks = db.query(TaskModel).all()

    total = len(tasks)
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}

    for task in tasks:
        if task.quadrant in by_quadrant:
            by_quadrant[task.quadrant] += 1
        if task.completed:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1

    return {
        "total_tasks": total,
        "by_quadrant": by_quadrant,
        "by_status": by_status,
    }