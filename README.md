# LLM API

Учебное API-приложение на Python и FastAPI, которое создаёт структурированные учебные планы с помощью локальной языковой модели через Ollama.

## Возможности

- принимает тему и температуру генерации;
- обращается к локальной модели через OpenAI-совместимый API;
- возвращает структурированный JSON;
- проверяет запросы и ответы через Pydantic;
- обрабатывает ошибки подключения и валидации.

## Технологии

- Python
- FastAPI
- Pydantic
- OpenAI Python SDK
- Ollama
- Qwen3 1.7B

## Установка

Создать виртуальное окружение:

```powershell
python -m venv .venv
```

Активировать окружение:

```powershell
.venv\Scripts\Activate.ps1
```

Установить зависимости:

```powershell
python -m pip install -r requirements.txt
```

## Подготовка Ollama

Установить Ollama:

https://ollama.com/download/windows

Загрузить модель:

```powershell
ollama pull qwen3:1.7b
```

## Запуск

Запустить Ollama через меню «Пуск».

Запустить FastAPI:

```powershell
uvicorn main:app --reload --port 8001
```

Открыть Swagger:

```text
http://127.0.0.1:8001/docs
```

## Пример запроса

```json
{
  "topic": "Основы Python",
  "temperature": 0.3
}
```

## Пример ответа

```json
{
  "topic": "Основы Python",
  "temperature": 0.3,
  "plan": {
    "title": "Учебный план по Python",
    "description": "План изучения основных возможностей Python",
    "steps": [
      "Изучить переменные",
      "Разобрать условия",
      "Освоить циклы"
    ],
    "estimated_hours": 10
  }
}
```

## Коды ответа

- `200` — успешный запрос;
- `422` — неправильные входные данные;
- `502` — модель вернула неправильную структуру;
- `503` — Ollama недоступна.