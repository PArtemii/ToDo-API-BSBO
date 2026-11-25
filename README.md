# ToDo-API-BSBO

## Краткое описание
API для управления задачами с классификацией по матрице Эйзенхауэра.  
Поддерживает получение списка задач, фильтрацию по квадрантам и статусу, поиск по ключевому слову, а также вывод статистики.

## Технологии
- Python
- FastAPI
- Uvicorn
- Git

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
5. Открыть в браузере `http://127.0.0.1:8000/docs` для просмотра интерактивной документации.

## Автор
Пугач Артемий Юрьевич