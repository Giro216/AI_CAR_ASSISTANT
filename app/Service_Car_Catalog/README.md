# Service Car Catalog

Сервис каталога автомобилей (FastAPI). Пока без БД: репозиторий реализован в памяти как заглушка под последующую замену
на SQLAlchemy/другой источник.

## Переменные окружения (изображения)

Для получения фото используется Serper API:

- `SERPER_API_KEY` — API key
- `RUN_REAL_SERPER_TESTS` — Флаг для запуска реальных тестов (по умолчанию `false`)

Если переменные не заданы — поле `imageUrl` будет `null`.

## Запуск

```powershell
Set-Location "C:\Users\maks0\source\4_course\Diplom\AI_Car_Assistant\app\Service_Car_Catalog"
python -m uvicorn main:app --reload
```

Swagger будет доступен на: `http://127.0.0.1:8000/docs`

## API

Базовый префикс: `/api/v1/cars`

- `GET /api/v1/cars`
- `GET /api/v1/cars/{car_id}`
- `GET /api/v1/cars/popular`
- `GET /api/v1/cars/search?q=...`
- `GET /api/v1/cars/filters/meta`
- `GET /api/v1/cars/{car_id}/similar`
- `GET /api/v1/cars/{car_id}/pricing`

