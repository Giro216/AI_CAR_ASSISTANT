"""Конфигурация pytest для тестирования.

Содержит фикстуры для:
- Тестовой БД
- Mock сервисов
- Тестовых клиентов
"""

import pytest
import sys
from pathlib import Path

# Добавляем проект в PATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.service.MockImageService import MockImageService
from app.repository.InMemoryCarsRepository import InMemoryCarsRepository
from app.repository.SQLAlchemyCarsRepository import SQLAlchemyCarsRepository
from app.service.carService import CarService


# ============================================================================
# ФИКСТУРЫ ДЛЯ ТЕСТОВОЙ БД
# ============================================================================

@pytest.fixture(scope="session")
def test_db_engine():
    """Создаем тестовую БД в памяти (SQLite)."""
    # Используем SQLite с StaticPool для тестирования
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    
    return engine


@pytest.fixture(scope="session")
def test_session_factory(test_db_engine):
    """Создаем factory для создания сессий."""
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine,
    )
    return SessionLocal


@pytest.fixture
def test_db_session(test_session_factory, test_db_engine) -> Session:
    """Фикстура для получения сессии БД в тесте.
    
    Автоматически откатывает все изменения после теста.
    """
    # Очищаем все таблицы перед тестом
    Base.metadata.drop_all(bind=test_db_engine)
    Base.metadata.create_all(bind=test_db_engine)
    
    session = test_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ============================================================================
# ФИКСТУРЫ ДЛЯ MOCK СЕРВИСОВ
# ============================================================================

@pytest.fixture
def mock_image_service():
    """Mock сервис изображений - не делает реальные API запросы."""
    return MockImageService()


@pytest.fixture
def mock_image_service_fail():
    """Mock сервис в режиме ошибки."""
    return MockImageService(fail_mode=True)


@pytest.fixture
def in_memory_repository():
    """In-memory репозиторий для тестов."""
    return InMemoryCarsRepository()


# ============================================================================
# ФИКСТУРЫ ДЛЯ РЕПОЗИТОРИЕВ
# ============================================================================

@pytest.fixture
def sql_repository(test_db_session):
    """SQL репозиторий с тестовой БД."""
    return SQLAlchemyCarsRepository(session=test_db_session)


# ============================================================================
# ФИКСТУРЫ ДЛЯ СЕРВИСОВ
# ============================================================================

@pytest.fixture
def car_service_with_mock(in_memory_repository, mock_image_service):
    """CarService с mock зависимостями (для unit тестов)."""
    return CarService(repo=in_memory_repository, image_service=mock_image_service)


@pytest.fixture
def car_service_with_db(sql_repository, mock_image_service):
    """CarService с реальной БД и mock image service (для БД тестов)."""
    return CarService(repo=sql_repository, image_service=mock_image_service)


# ============================================================================
# МАРКЕРЫ PYTEST
# ============================================================================

def pytest_configure(config):
    """Регистрируем custom маркеры."""
    config.addinivalue_line(
        "markers", "db: тесты работы с БД"
    )
    config.addinivalue_line(
        "markers", "unit: unit тесты (без БД)"
    )
    config.addinivalue_line(
        "markers", "integration: интеграционные тесты (требуют реальный API)"
    )


