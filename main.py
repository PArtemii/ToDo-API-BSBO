from fastapi import FastAPI
from database import engine, Base
from routers import tasks, stats

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={"name": "Пугач Артемий Юрьевич"},
)

# Сначала подключается stats, чтобы /tasks/stats не перехватывался /tasks/{task_id}
app.include_router(stats.router)
app.include_router(tasks.router)


@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "api_title": app.title,
        "api_description": app.description,
        "api_version": app.version,
        "api_author": app.contact["name"],
    }