from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db
from models import Task  # noqa: F401
from routers import tasks, stats
from scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск приложения...")
    print("Инициализация базы данных...")
    await init_db()
    print("База данных инициализирована!")

    scheduler = start_scheduler()
    print("Приложение готово к работе!")
    yield

    print("Остановка планировщика...")
    scheduler.shutdown()
    print("Остановка приложения...")


app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="2.1.0",
    contact={"name": "Пугач Артемий Юрьевич"},
    lifespan=lifespan,
)

app.include_router(tasks.router)
app.include_router(stats.router)


@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "api_title": app.title,
        "api_description": app.description,
        "api_version": app.version,
        "api_author": app.contact["name"],
    }