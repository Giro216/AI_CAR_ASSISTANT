# Service_Gateway_Api

Минимальный API Gateway на FastAPI: принимает запросы и проксирует их в нужный микросервис по префиксу пути.

## Быстрый старт (локально)

1) Установить зависимости:

```bash
pip install -r requirements.txt
```

2) Запустить сервис-каталог на другом порту (пример):

```bash
# в папке Service_Car_Catalog
uvicorn main:app --reload --port 8001
```

3) Запустить gateway:

```bash
# в папке Service_Gateway_Api
setx GATEWAY_ROUTES "{\"/api/v1/cars\":\"http://localhost:8001\"}"
uvicorn main:app --reload --port 8000
```

После этого запросы в `http://localhost:8000/api/v1/cars/...` будут уходить в каталог.

## Конфигурация

- `GATEWAY_ROUTES` — JSON-словарь `{"/path/prefix": "http://host:port"}`.
  Gateway выбирает *самый длинный* подходящий префикс.

Пример:

```json
{
  "/api/v1/cars": "http://localhost:8001",
  "/api/v1/chat": "http://localhost:8002",
  "/api/v1/users": "http://localhost:8003"
}
```

- `GATEWAY_CORS_ORIGINS` — (опционально) origins через запятую.
