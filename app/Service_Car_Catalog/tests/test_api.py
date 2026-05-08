import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import main
from app.service.MockImageService import MockImageService
from app.repository.InMemoryCarsRepository import InMemoryCarsRepository
from app.service.carService import CarService
from app.config.dependency import get_image_service, get_cars_repository, get_car_service

# Создаем mock сервис для тестов (не делает реальные запросы к API)
mock_image_service = MockImageService()

mock_repository = InMemoryCarsRepository()

# Создаем сервис с mock зависимостями
mock_car_service = CarService(repo=mock_repository, image_service=mock_image_service)

# Переопределяем ВСЕ зависимости на mock версии
# Так тесты не будут делать реальные запросы к API или БД
main.app.dependency_overrides[get_image_service] = lambda: mock_image_service
main.app.dependency_overrides[get_cars_repository] = lambda: mock_repository
main.app.dependency_overrides[get_car_service] = lambda: mock_car_service

client = TestClient(main.app)


def assert_model_card_payload(item: dict) -> None:
    assert {"id", "brand_model_id", "brand", "model", "start_year", "end_year", "imageUrl", "imageMeta", "isPopular"}.issubset(
        item.keys()
    )
    if item.get("imageMeta"):
        assert item["imageMeta"]["link"] is not None
        assert item["imageMeta"]["imageUrl"] is not None


@pytest.mark.unit
def test_list_cars():
    r = client.get("/api/v1/cars")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_model_card_payload(data[0])


@pytest.mark.unit
def test_car_detail_ok():
    r = client.get("/api/v1/cars/1/sedan/details")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "1"
    assert data["brand_model_id"] == "1"
    assert {"id", "brand_model_id", "brand", "model"}.issubset(data.keys())


@pytest.mark.unit
def test_car_detail_404():
    r = client.get("/api/v1/cars/does-not-exist/sedan/details")
    assert r.status_code == 404


@pytest.mark.unit
def test_generations_by_brand_model_id():
    r = client.get("/api/v1/cars/1/generations")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert {"id", "brand_model_id", "brand", "model"}.issubset(data[0].keys())
    assert all(item["brand_model_id"] == "1" for item in data)


@pytest.mark.unit
def test_filters_meta():
    r = client.get("/api/v1/cars/filters/meta")
    assert r.status_code == 200
    data = r.json()
    assert {"bodyTypes", "fuels", "transmissions", "brands"}.issubset(data.keys())


@pytest.mark.unit
def test_search():
    r = client.get("/api/v1/cars/search", params={"q": "toy"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_model_card_payload(data[0])


@pytest.mark.unit
def test_popular_cars():
    r = client.get("/api/v1/cars/popular")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_model_card_payload(data[0])
    assert data[0]["isPopular"] is True


@pytest.mark.unit
@pytest.mark.skip(reason="pricing endpoint is currently disabled")
def test_pricing_stub():
    r = client.get("/api/v1/cars/1/pricing")
    assert r.status_code == 200
    data = r.json()
    assert data["carId"] == "1"
    assert "history" in data


@pytest.mark.unit
def test_list_cars_with_images_no_api_calls():
    """Проверка что список машин получает изображения без реальных запросов к API.
    
    Тест гарантирует, что используется mock сервис и токены не расходуются.
    """
    mock_image_service.reset()

    r = client.get("/api/v1/cars")
    assert r.status_code == 200
    data = r.json()

    # Проверяем что получили список с изображениями
    assert isinstance(data, list)
    assert len(data) >= 1

    # Проверяем что в ответе есть поле изображения
    assert_model_card_payload(data[0])


@pytest.mark.unit
def test_car_detail_with_image_no_api_calls():
    """Проверка что детальная карточка машины получает изображение без реальных запросов.
    
    Тест гарантирует, что используется mock сервис и токены не расходуются.
    """
    mock_image_service.reset()

    r = client.get("/api/v1/cars/1/sedan/details")
    assert r.status_code == 200
    data = r.json()

    assert data["id"] == "1"
    assert "imageMeta" in data

    # Если imageMeta не None, проверяем что link не пустой
    if data.get("imageMeta"):
        assert data["imageMeta"]["link"] is not None


@pytest.mark.unit
def test_mock_service_returns_non_null_link():
    """Проверка что mock сервис возвращает валидные ссылки."""
    import asyncio

    result = asyncio.run(mock_image_service.get_image("test car"))

    assert result is not None
    assert result.link is not None
    assert result.link != ""
    assert result.imageUrl is not None
    assert result.imageUrl != ""


@pytest.mark.unit
def test_mock_service_call_counting():
    """Проверка что можно отследить количество вызовов mock сервиса."""
    mock_image_service.reset()
    assert mock_image_service.get_call_count() == 0

    import asyncio
    asyncio.run(mock_image_service.get_image("car 1"))
    assert mock_image_service.get_call_count() == 1

    asyncio.run(mock_image_service.get_image("car 2"))
    assert mock_image_service.get_call_count() == 2


@pytest.mark.unit
def test_mock_service_fail_mode():
    """Проверка режима имитации ошибки."""
    fail_service = MockImageService(fail_mode=True)

    import asyncio
    result = asyncio.run(fail_service.get_image("test car"))

    assert result is None
    r = client.get("/api/v1/cars")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_model_card_payload(data[0])
