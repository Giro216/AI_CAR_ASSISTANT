from typing import List, Optional

from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity


# TODO переделать CarGenerationEntity -> CarModelEntity
class InMemoryCarsRepository:
    def __init__(self) -> None:
        self._cars: List[CarGenEntity] = [
            CarGenEntity(id="1", brand="Toyota", model="Camry", year_from=2015, year_to=2024, body_type="sedan",
                         fuel="gasoline",
                         transmission="automatic"),
            CarGenEntity(id="2", brand="Toyota", model="RAV4", year_from=2016, year_to=2024, body_type="suv",
                         fuel="gasoline",
                         transmission="automatic"),
            CarGenEntity(id="3", brand="BMW", model="X5", year_from=2010, year_to=2024, body_type="suv",
                         fuel="diesel",
                         transmission="automatic"),
            CarGenEntity(id="4", brand="Kia", model="Rio", year_from=2012, year_to=2024, body_type="sedan",
                         fuel="gasoline",
                         transmission="automatic"),
        ]

    def list_models(
            self,
            *,
            brand: Optional[str] = None,
            model: Optional[str] = None,
            sort: Optional[str] = None
    ) -> List[CarModelEntity]:
        return self.unique_models_by_year(brand=brand, model=model)

    def list_gens(
            self,
            *,
            brand: Optional[str] = None,
            model: Optional[str] = None,
            sort: Optional[str] = None
    ) -> List[CarGenEntity]:
        items = self._cars
        if brand:
            items = [c for c in items if c.brand.lower() == brand.lower()]
        if model:
            items = [c for c in items if c.model.lower() == model.lower()]
        return list(items)

    def get_by_id(self, car_id: str):
        return next((c for c in self._cars if c.id == car_id), None)

    def search_models(self, q: str, *, limit: int = 20) -> List[CarModelEntity]:
        qq = q.lower()
        items = self.unique_models_by_year()
        return [
                   c for c in items
                   if qq in c.brand.lower() or qq in c.model.lower()
               ][:limit]

    def popular(self, *, limit: int = 10) -> List[CarModelEntity]:
        return self.unique_models_by_year()[:limit]

    def similar(self, car_id: str, *, limit: int = 10) -> List[CarModelEntity]:
        base = self.get_by_id(car_id)
        if not base:
            return []
        items = [
            c for c in self.unique_models_by_year()
            if c.brand == base.brand and c.model != base.model
        ]
        return items[:limit]

    def unique_models_by_year(
            self,
            *,
            brand: Optional[str] = None,
            model: Optional[str] = None
    ) -> List[CarModelEntity]:
        items = self._cars
        if brand:
            items = [c for c in items if c.brand.lower() == brand.lower()]
        if model:
            items = [c for c in items if c.model.lower() == model.lower()]
        unique = {}
        for c in items:
            key = (c.brand, c.model)
            if key not in unique or (
                    c.year_from is not None and (
                    unique[key].start_year is None or c.year_from < unique[key].start_year)):
                unique[key] = CarModelEntity(
                    id=str(c.id),
                    brand=c.brand,
                    model=c.model,
                    start_year=c.year_from,
                    end_year=c.year_to,
                )
        return sorted(unique.values(),
                      key=lambda x: (x.start_year if x.start_year is not None else 10 ** 9, x.brand, x.model))
