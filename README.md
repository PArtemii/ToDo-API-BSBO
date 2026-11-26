# ToDo-API-BSBO

## Краткое описание
API для управления задачами с классификацией по матрице Эйзенхауэра.  
Поддерживает получение списка задач, фильтрацию по квадрантам и статусу, поиск по ключевому слову, вывод статистики и демонстрационный POST-запрос.

## Технологии
- Python
- FastAPI
- Uvicorn
- Git

## Структура проекта
```text
ToDo-API-BSBO/
├── routers/
│   ├── __init__.py
│   ├── tasks.py
│   └── stats.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Инструкция по запуску
1. Клонировать репозиторий:
    ```bash
    git clone https://github.com/PArtemii/ToDo-API-BSBO.git
    cd ToDo-API-BSBO
    ```
2. Создать и активировать виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/Scripts/activate
    ```
    Для Linux/macOS:
    ```bash
    source venv/bin/activate
    ```
3. Установить зависимости:
    ```bash
    pip install -r requirements.txt
    ```
4. Запустить приложение:
    ```bash
    uvicorn main:app --reload
    ```
5. Открыть Swagger UI: `http://127.0.0.1:8000/docs`
   Открыть ReDoc: `http://127.0.0.1:8000/redoc`

## Автор
Пугач Артемий Юрьевич