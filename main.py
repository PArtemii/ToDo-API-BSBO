from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db
from models import Task, User  # noqa: F401
from routers import tasks, stats, auth
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
    version="3.0.0",
    contact={"name": "Пугач Артемий Юрьевич"},
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/api/v3")
app.include_router(tasks.router, prefix="/api/v3")
app.include_router(stats.router, prefix="/api/v3")


@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Task Manager API - Управление задачами",
        "version": app.version,
        "database": "PostgreSQL (Supabase)",
        "docs": "/docs",
        "redoc": "/redoc",
    }