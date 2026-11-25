from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={"name": "Пугач Артемий Юрьевич"}
)

tasks_db = [
    {
        "id": 1,
        "title": "Сдать отчёт по интероперабельности",
        "description": "Подготовить отчёт по проекту и презентацию",
        "quadrant": "Q1",
        "completed": False,
    },
    {
        "id": 2,
        "title": "Изучить FastAPI",
        "description": "Прочитать документацию и выполнить практику",
        "quadrant": "Q2",
        "completed": True,
    },
    {
        "id": 3,
        "title": "Ответить на письма",
        "description": "Рутинная работа с почтой",
        "quadrant": "Q3",
        "completed": False,
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Отдых и восстановление",
        "quadrant": "Q4",
        "completed": False,
    },
]


@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "app_title": app.title,
        "app_description": app.description,
        "app_version": app.version,
        "app_contact": app.contact,
    }


@app.get("/tasks")
async def get_all_tasks() -> dict:
    return {"count": len(tasks_db), "tasks": tasks_db}


@app.get("/tasks/stats")
async def get_tasks_stats() -> dict:
    total = len(tasks_db)
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}

    for task in tasks_db:
        quadrant = task["quadrant"]
        if quadrant in by_quadrant:
            by_quadrant[quadrant] += 1
        if task["completed"]:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1

    return {
        "total_tasks": total,
        "by_quadrant": by_quadrant,
        "by_status": by_status,
    }


@app.get("/tasks/search")
async def search_tasks(q: str) -> dict:
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Поисковый запрос должен содержать минимум 2 символа",
        )

    q_lower = q.lower()
    results = [
        task
        for task in tasks_db
        if q_lower in task["title"].lower()
        or q_lower in task["description"].lower()
    ]

    if not results:
        raise HTTPException(status_code=404, detail="Задачи не найдены")

    return {"query": q, "count": len(results), "tasks": results}


@app.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="Статус не найден. Используйте: completed или pending",
        )

    filtered = [
        task
        for task in tasks_db
        if (task["completed"] and status == "completed")
        or (not task["completed"] and status == "pending")
    ]

    return {"status": status, "count": len(filtered), "tasks": filtered}


@app.get("/tasks/quadrant/{quadrant}")
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


@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Задача не найдена")

# Также в коде добавлены эндпоинты статистики, фильтрации по статусу и поиска, исправлен порядок маршрутов