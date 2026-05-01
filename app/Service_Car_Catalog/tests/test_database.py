"""Тесты работы с БД.

Эти тесты используют реальную БД (SQLite для тестирования).
Отмечены маркером @pytest.mark.db для отделения от unit тестов.

Запуск:
    # Все тесты
    pytest tests/test_database.py -v
    
    # Только БД тесты
    pytest -m db -v
    
    # Все кроме БД тестов
    pytest -m "not db" -v
"""

import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.CarModel import CarModel
from app.entity.CarEntity import CarEntity
from app.repository.SQLAlchemyCarsRepository import SQLAlchemyCarsRepository


# ============================================================================
# ФИКСТУРЫ ДЛЯ ПОДГОТОВКИ ДАННЫХ
# ============================================================================

@pytest.fixture
def sample_cars(test_db_session):
    """Добавляет тестовые автомобили в БД."""
    cars = [
        CarModel(
            id=1,
            make="Toyota",
            model="Camry",
            year_from=2015,
            year_to=2024,
            body_type="sedan",
            engine_type="gasoline",
            transmission_type="automatic",
        ),
        CarModel(
            id=2,
            make="Toyota",
            model="RAV4",
            year_from=2016,
            year_to=2024,
            body_type="suv",
            engine_type="gasoline",
            transmission_type="automatic",
        ),
        CarModel(
            id=3,
            make="BMW",
            model="X5",
            year_from=2010,
            year_to=2024,
            body_type="suv",
            engine_type="diesel",
            transmission_type="automatic",
        ),
        CarModel(
            id=4,
            make="Kia",
            model="Rio",
            year_from=2012,
            year_to=2024,
            body_type="sedan",
            engine_type="gasoline",
            transmission_type="manual",
        ),
        CarModel(
            id=5,
            make="Mercedes",
            model="E-Class",
            year_from=2018,
            year_to=2024,
            body_type="sedan",
            engine_type="gasoline",
            transmission_type="automatic",
        ),
    ]
    
    for car in cars:
        test_db_session.add(car)
    
    test_db_session.commit()
    return cars


# ============================================================================
# ТЕСТЫ РЕПОЗИТОРИЯ БД
# ============================================================================

@pytest.mark.db
class TestSQLAlchemyCarsRepository:
    """Тесты SQLAlchemyCarsRepository."""
    
    def test_list_all_cars(self, sql_repository, sample_cars, test_db_session):
        """Тест получения всех автомобилей."""
        result = sql_repository.list()
        
        assert len(result) == 5
        assert all(isinstance(car, CarEntity) for car in result)
        assert result[0].brand == "Toyota"
    
    def test_list_by_brand(self, sql_repository, sample_cars, test_db_session):
        """Тест фильтрации по марке."""
        result = sql_repository.list(brand="Toyota")
        
        assert len(result) == 2
        assert all(car.brand == "Toyota" for car in result)
    
    def test_list_by_brand_case_insensitive(self, sql_repository, sample_cars, test_db_session):
        """Тест фильтрации по марке без учета регистра."""
        result = sql_repository.list(brand="toyota")
        
        assert len(result) == 2
        assert result[0].brand == "Toyota"
    
    def test_list_by_model(self, sql_repository, sample_cars, test_db_session):
        """Тест фильтрации по модели."""
        result = sql_repository.list(model="Camry")
        
        assert len(result) == 1
        assert result[0].model == "Camry"
    
    def test_list_by_brand_and_model(self, sql_repository, sample_cars, test_db_session):
        """Тест фильтрации по марке и модели."""
        result = sql_repository.list(brand="Toyota", model="RAV4")
        
        assert len(result) == 1
        assert result[0].brand == "Toyota"
        assert result[0].model == "RAV4"
    
    def test_list_nonexistent_brand(self, sql_repository, sample_cars, test_db_session):
        """Тест поиска несуществующей марки."""
        result = sql_repository.list(brand="Lamborghini")
        
        assert len(result) == 0
    
    def test_get_by_id(self, sql_repository, sample_cars, test_db_session):
        """Тест получения автомобиля по ID."""
        result = sql_repository.get_by_id("1")
        
        assert result is not None
        assert isinstance(result, CarEntity)
        assert result.id == "1"
        assert result.brand == "Toyota"
        assert result.model == "Camry"
    
    def test_get_by_id_nonexistent(self, sql_repository, sample_cars, test_db_session):
        """Тест получения несуществующего автомобиля."""
        result = sql_repository.get_by_id("999")
        
        assert result is None
    
    def test_search_by_brand(self, sql_repository, sample_cars, test_db_session):
        """Тест поиска по части названия марки."""
        result = sql_repository.search("toy", limit=20)
        
        assert len(result) == 2
        assert all(car.brand == "Toyota" for car in result)
    
    def test_search_by_model(self, sql_repository, sample_cars, test_db_session):
        """Тест поиска по части названия модели."""
        result = sql_repository.search("camry", limit=20)
        
        assert len(result) == 1
        assert result[0].model == "Camry"
    
    def test_search_case_insensitive(self, sql_repository, sample_cars, test_db_session):
        """Тест поиска без учета регистра."""
        result = sql_repository.search("MERCEDES", limit=20)
        
        assert len(result) == 1
        assert result[0].brand == "Mercedes"
    
    def test_search_with_limit(self, sql_repository, sample_cars, test_db_session):
        """Тест поиска с ограничением результатов."""
        result = sql_repository.search("", limit=2)
        
        assert len(result) <= 2
    
    def test_popular_returns_cars(self, sql_repository, sample_cars, test_db_session):
        """Тест получения популярных автомобилей."""
        result = sql_repository.popular(limit=3)
        
        assert len(result) == 3
        assert all(isinstance(car, CarEntity) for car in result)
    
    def test_popular_with_limit(self, sql_repository, sample_cars, test_db_session):
        """Тест ограничения количества популярных авто."""
        result = sql_repository.popular(limit=2)
        
        assert len(result) == 2
    
    def test_similar_cars(self, sql_repository, sample_cars, test_db_session):
        """Тест получения похожих автомобилей."""
        # Ищем похожие на Toyota Camry (sedan)
        result = sql_repository.similar(car_id="1", limit=10)
        
        # Должны найти другие седаны
        assert len(result) > 0
        # Сам автомобиль не должен быть в результатах
        assert not any(car.id == "1" for car in result)
    
    def test_similar_nonexistent_car(self, sql_repository, sample_cars, test_db_session):
        """Тест похожих авто для несуществующего ID."""
        result = sql_repository.similar(car_id="999", limit=10)
        
        assert len(result) == 0


# ============================================================================
# ТЕСТЫ ПРЕОБРАЗОВАНИЯ ДАННЫХ
# ============================================================================

@pytest.mark.db
class TestCarModelConversion:
    """Тесты преобразования CarModel в CarEntity."""
    
    def test_car_model_to_entity(self, sample_cars, test_db_session):
        """Тест преобразования модели в сущность."""
        car = test_db_session.query(CarModel).first()
        entity = car.to_entity
        
        assert isinstance(entity, CarEntity)
        assert entity.id == "1"
        assert entity.brand == "Toyota"
        assert entity.model == "Camry"
        assert entity.body_type == "sedan"
        assert entity.fuel == "gasoline"
    
    def test_entity_fields_mapping(self, sample_cars, test_db_session):
        """Тест что все поля корректно преобразуются."""
        car = test_db_session.query(CarModel).filter_by(id=3).first()
        entity = car.to_entity
        
        assert entity.id == "3"
        assert entity.brand == "BMW"
        assert entity.model == "X5"
        assert entity.year_from == 2010
        assert entity.year_to == 2024
        assert entity.body_type == "suv"
        assert entity.fuel == "diesel"
        assert entity.transmission == "automatic"


# ============================================================================
# ТЕСТЫ ИНТЕГРАЦИИ С СЕРВИСОМ
# ============================================================================

@pytest.mark.db
class TestCarServiceWithDatabase:
    """Тесты CarService с реальной БД."""
    
    @pytest.mark.asyncio
    async def test_get_cars_from_db(self, car_service_with_db, sample_cars):
        """Тест получения авто из БД через сервис."""
        result = await car_service_with_db.get_cars()
        
        assert len(result) == 5
        assert result[0].brand == "Toyota"
    
    @pytest.mark.asyncio
    async def test_get_cars_with_filter(self, car_service_with_db, sample_cars):
        """Тест фильтрации авто из БД через сервис."""
        result = await car_service_with_db.get_cars(brand="BMW")
        
        assert len(result) == 1
        assert result[0].brand == "BMW"
        assert result[0].model == "X5"
    
    @pytest.mark.asyncio
    async def test_get_car_detail_from_db(self, car_service_with_db, sample_cars):
        """Тест получения деталей авто из БД."""
        result = await car_service_with_db.get_car_detail(car_id="2")
        
        assert result.id == "2"
        assert result.brand == "Toyota"
        assert result.model == "RAV4"
    
    @pytest.mark.asyncio
    async def test_get_car_detail_not_found(self, car_service_with_db, sample_cars):
        """Тест 404 при поиске несуществующего авто."""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await car_service_with_db.get_car_detail(car_id="999")
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_search_from_db(self, car_service_with_db, sample_cars):
        """Тест поиска авто из БД."""
        result = await car_service_with_db.search(q="camry")
        
        assert len(result) == 1
        assert result[0].model == "Camry"
    
    @pytest.mark.asyncio
    async def test_get_filters_meta_from_db(self, car_service_with_db, sample_cars):
        """Тест получения метаданных фильтров из БД."""
        result = await car_service_with_db.get_filters_meta()
        
        assert "sedan" in result.bodyTypes
        assert "suv" in result.bodyTypes
        assert "gasoline" in result.fuels
        assert "diesel" in result.fuels
        assert "Toyota" in result.brands
        assert "BMW" in result.brands


# ============================================================================
# ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ
# ============================================================================

@pytest.mark.db
class TestEdgeCases:
    """Тесты граничных случаев при работе с БД."""
    
    def test_empty_database(self, sql_repository, test_db_session):
        """Тест работы репозитория с пустой БД."""
        result = sql_repository.list()
        assert len(result) == 0
    
    def test_search_empty_query(self, sql_repository, sample_cars, test_db_session):
        """Тест поиска с пустым запросом."""
        result = sql_repository.search("", limit=20)
        
        # Пустой запрос может вернуть все или ничего в зависимости от реализации
        assert isinstance(result, list)
    
    def test_get_by_id_empty_string(self, sql_repository, sample_cars, test_db_session):
        """Тест получения по пустому ID."""
        result = sql_repository.get_by_id("")
        
        assert result is None
    
    def test_special_characters_in_search(self, sql_repository, sample_cars, test_db_session):
        """Тест поиска со специальными символами."""
        result = sql_repository.search("% ' \" \\", limit=20)
        
        # Должен обработать без ошибок (возможно, 0 результатов)
        assert isinstance(result, list)


# ============================================================================
# ИНСТРУКЦИИ ПО ЗАПУСКУ
# ============================================================================

"""
ЗАПУСК ТЕСТОВ БД:

1. Только тесты БД:
   pytest tests/test_database.py -v

2. По маркеру:
   pytest -m db -v

3. Все тесты КРОМЕ БД (unit тесты):
   pytest -m "not db" -v

4. С подробным выводом:
   pytest tests/test_database.py -v -s

5. С покрытием:
   pytest tests/test_database.py --cov=app --cov-report=html

ОСОБЕННОСТИ:

- Каждый тест использует отдельную сессию БД
- БД автоматически откатывается после каждого теста (rollback)
- Используется SQLite in-memory для скорости
- Не требует реального PostgreSQL для запуска тестов
- Все тесты полностью изолированы друг от друга
"""

