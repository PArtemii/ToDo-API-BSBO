from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db
from models import Task  # noqa: F401 — импорт нужен для регистрации модели в Base
from routers import tasks, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={"name": "Пугач Артемий Юрьевич"},
    lifespan=lifespan,
)

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