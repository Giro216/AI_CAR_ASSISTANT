from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.entity.CarEntity import CarEntity


class CarsRepository(ABC):
    @abstractmethod
    def list(self, *, brand: Optional[str] = None, model: Optional[str] = None, sort: Optional[str] = None) -> List[
        CarEntity]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, car_id: str) -> Optional[CarEntity]:
        raise NotImplementedError

    @abstractmethod
    def search(self, q: str, *, limit: int = 20) -> List[CarEntity]:
        raise NotImplementedError

    @abstractmethod
    def popular(self, *, limit: int = 10) -> List[CarEntity]:
        raise NotImplementedError

    @abstractmethod
    def similar(self, car_id: str, *, limit: int = 10) -> List[CarEntity]:
        raise NotImplementedError


class InMemoryCarsRepository(CarsRepository):
    """Временная реализация репозитория без БД (заглушка).

    Позже заменить на SQLAlchemyCarsRepository / ExternalCarsRepository и т.п.
    """

    def __init__(self) -> None:
        self._cars: List[CarEntity] = [
            CarEntity(id="1", brand="Toyota", model="Camry", year=2020, body_type="sedan", fuel="gasoline",
                      transmission="automatic"),
            CarEntity(id="2", brand="Toyota", model="RAV4", year=2021, body_type="suv", fuel="gasoline",
                      transmission="automatic"),
            CarEntity(id="3", brand="BMW", model="X5", year=2019, body_type="suv", fuel="diesel",
                      transmission="automatic"),
            CarEntity(id="4", brand="Kia", model="Rio", year=2018, body_type="sedan", fuel="gasoline",
                      transmission="automatic"),
        ]

    def list(self, *, brand: Optional[str] = None, model: Optional[str] = None, sort: Optional[str] = None) -> List[
        CarEntity]:
        items = self._cars
        if brand:
            items = [c for c in items if c.brand.lower() == brand.lower()]
        if model:
            items = [c for c in items if c.model.lower() == model.lower()]
        # sort пока заглушка
        return list(items)

    def get_by_id(self, car_id: str) -> Optional[CarEntity]:
        for c in self._cars:
            if c.id == car_id:
                return c
        return None

    def search(self, q: str, *, limit: int = 20) -> List[CarEntity]:
        qq = q.lower().strip()
        res = [c for c in self._cars if
               qq in c.brand.lower() or qq in c.model.lower() or qq in f"{c.brand} {c.model}".lower()]
        return res[:limit]

    def popular(self, *, limit: int = 10) -> List[CarEntity]:
        # Заглушка: первые N
        return self._cars[:limit]

    def similar(self, car_id: str, *, limit: int = 10) -> List[CarEntity]:
        base = self.get_by_id(car_id)
        if not base:
            return []
        # Заглушка: похожие по бренду или типу кузова
        candidates = [c for c in self._cars if
                      c.id != car_id and (c.brand == base.brand or (base.body_type and c.body_type == base.body_type))]
        return candidates[:limit]
