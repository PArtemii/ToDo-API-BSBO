from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)

# Временное хранилище, позже будет заменено на базу данных
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": "Лекция по интероперабельности",
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now(),
    },
]


@router.get("/")
async def get_all_tasks() -> dict:
    return {"count": len(tasks_db), "tasks": tasks_db}


@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4",
        )

    filtered_tasks = [
        task for task in tasks_db if task["quadrant"] == quadrant
    ]

    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks,
    }


@router.get("/search")
async def search_tasks(
    q: str = Query(..., min_length=2, description="Ключевое слово для поиска")
) -> dict:
    q_lower = q.lower()
    results = [
        task
        for task in tasks_db
        if q_lower in task["title"].lower()
        or (
            task["description"] is not None
            and q_lower in task["description"].lower()
        )
    ]

    if not results:
        raise HTTPException(status_code=404, detail="Задачи не найдены")

    return {"query": q, "count": len(results), "tasks": results}


@router.get("/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="Статус не найден. Используйте: completed или pending",
        )

    filtered = [
        task
        for task in tasks_db
        if task["completed"] == (status == "completed")
    ]

    return {"status": status, "count": len(filtered), "tasks": filtered}


@router.get("/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Задача не найдена")


@router.post("/")
async def create_task(task: dict) -> dict:
    return {"message": "Запись успешно создана!", "task": task}