from typing import List

from app.entity.CarEntity import CarEntity


class InMemoryCarsRepository:
    def __init__(self) -> None:
        self._cars: List[CarEntity] = [
            CarEntity(id="1", brand="Toyota", model="Camry", year_from=2015, year_to=2024, body_type="sedan", fuel="gasoline",
                      transmission="automatic"),
            CarEntity(id="2", brand="Toyota", model="RAV4", year_from=2016, year_to=2024, body_type="suv", fuel="gasoline",
                      transmission="automatic"),
            CarEntity(id="3", brand="BMW", model="X5", year_from=2010, year_to=2024, body_type="suv", fuel="diesel",
                      transmission="automatic"),
            CarEntity(id="4", brand="Kia", model="Rio", year_from=2012, year_to=2024, body_type="sedan", fuel="gasoline",
                      transmission="automatic"),
        ]

    def list(self, *, brand=None, model=None, sort=None):
        items = self._cars
        if brand:
            items = [c for c in items if c.brand.lower() == brand.lower()]
        if model:
            items = [c for c in items if c.model.lower() == model.lower()]
        return list(items)

    def get_by_id(self, car_id: str):
        return next((c for c in self._cars if c.id == car_id), None)

    def search(self, q: str, *, limit: int = 20):
        qq = q.lower()
        return [
            c for c in self._cars
            if qq in c.brand.lower() or qq in c.model.lower()
        ][:limit]

    def popular(self, *, limit: int = 10):
        return self._cars[:limit]

    def similar(self, car_id: str, *, limit: int = 10):
        base = self.get_by_id(car_id)
        if not base:
            return []
        return [
            c for c in self._cars
            if c.id != car_id and (c.brand == base.brand or c.body_type == base.body_type)
        ][:limit]
