from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import datetime, timezone
from models import Task, User, UserRole
from database import get_async_session
from dependencies import get_current_user
from schemas import TimingStatsResponse

router = APIRouter(
    prefix="/stats",
    tags=["statistics"],
)


@router.get("/", response_model=dict)
async def get_tasks_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    is_admin = current_user.role == UserRole.ADMIN
    filter_cond = [] if is_admin else [Task.user_id == current_user.id]

    total_result = await db.execute(select(func.count(Task.id)).where(*filter_cond))
    total_tasks = total_result.scalar()

    quadrant_result = await db.execute(
        select(Task.quadrant, func.count(Task.id).label("count"))
        .where(*filter_cond)
        .group_by(Task.quadrant)
    )
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for row in quadrant_result:
        by_quadrant[row.quadrant] = row.count

    status_result = await db.execute(
        select(
            func.count(case((Task.completed == True, 1))).label("completed"),
            func.count(case((Task.completed == False, 1))).label("pending"),
        ).where(*filter_cond)
    )
    status_row = status_result.one()
    by_status = {"completed": status_row.completed, "pending": status_row.pending}

    return {"total_tasks": total_tasks, "by_quadrant": by_quadrant, "by_status": by_status}


@router.get("/timing", response_model=TimingStatsResponse)
async def get_deadline_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> TimingStatsResponse:
    now_utc = datetime.now(timezone.utc)
    is_admin = current_user.role == UserRole.ADMIN
    filter_cond = [] if is_admin else [Task.user_id == current_user.id]

    statement = select(
        func.sum(
            case(
                ((Task.completed == True) & (Task.completed_at <= Task.deadline_at), 1),
                else_=0,
            )
        ).label("completed_on_time"),
        func.sum(
            case(
                ((Task.completed == True) & (Task.completed_at > Task.deadline_at), 1),
                else_=0,
            )
        ).label("completed_late"),
        func.sum(
            case(
                ((Task.completed == False) & (Task.deadline_at != None) & (Task.deadline_at > now_utc), 1),
                else_=0,
            )
        ).label("on_plan_pending"),
        func.sum(
            case(
                ((Task.completed == False) & (Task.deadline_at != None) & (Task.deadline_at <= now_utc), 1),
                else_=0,
            )
        ).label("overdue_pending"),
    ).where(*filter_cond).select_from(Task)

    result = await db.execute(statement)
    stats_row = result.one()

    return TimingStatsResponse(
        completed_on_time=stats_row.completed_on_time or 0,
        completed_late=stats_row.completed_late or 0,
        on_plan_pending=stats_row.on_plan_pending or 0,
        overtime_pending=stats_row.overdue_pending or 0,
    )