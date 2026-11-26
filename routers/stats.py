from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from database import get_async_session
from models import Task

router = APIRouter(
    prefix="/tasks",
    tags=["stats"],
)


@router.get("/stats")
async def get_tasks_stats(
    db: AsyncSession = Depends(get_async_session),
) -> dict:
    result = await db.execute(select(Task))
    tasks = result.scalars().all()

    total = len(tasks)
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}
    deadlines = {"overdue": 0, "due_today": 0, "due_soon": 0, "no_deadline": 0}

    today = datetime.now(timezone.utc).date()

    for task in tasks:
        if task.quadrant in by_quadrant:
            by_quadrant[task.quadrant] += 1
        if task.completed:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1

        if task.deadline is None:
            deadlines["no_deadline"] += 1
        else:
            days = (task.deadline.date() - today).days
            if not task.completed:
                if days < 0:
                    deadlines["overdue"] += 1
                elif days == 0:
                    deadlines["due_today"] += 1
                elif days <= 3:
                    deadlines["due_soon"] += 1

    return {
        "total_tasks": total,
        "by_quadrant": by_quadrant,
        "by_status": by_status,
        "deadlines": deadlines,
    }