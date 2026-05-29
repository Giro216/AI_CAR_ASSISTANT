from typing import List, Optional

from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity
from app.entity.FiltersEntity import FiltersEntity


# TODO переделать CarGenerationEntity -> CarModelEntity
class InMemoryCarsRepository:
	def __init__(self) -> None:
		self._cars: List[CarGenEntity] = [
			CarGenEntity(id="1", brand_model_id="1", brand="Toyota", model="Camry", generation="XV70",
			             gen_comment="2017-2024", year_from=2015, year_to=2024, body_type="sedan"),
			CarGenEntity(id="2", brand_model_id="2", brand="Toyota", model="RAV4", generation="XA50",
			             gen_comment="2018-2024", year_from=2016, year_to=2024, body_type="suv"),
			CarGenEntity(id="3", brand_model_id="3", brand="BMW", model="X5", generation="G05",
			             gen_comment="2018-2024", year_from=2010, year_to=2024, body_type="suv"),
			CarGenEntity(id="4", brand_model_id="4", brand="Kia", model="Rio", generation="FB",
			             gen_comment="2017-2024", year_from=2012, year_to=2024, body_type="sedan"),
		]

	def list_models(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None,
			sort: Optional[str] = None,
			limit: int = 50,
			offset: int = 0
	) -> List[CarModelEntity]:
		return self.unique_models_by_year(brand_model_id=brand_model_id, brand=brand, model=model, limit=limit,
		                                  offset=offset)

	def count_models(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None
	) -> int:
		items = self.unique_models_by_year(brand_model_id=brand_model_id, brand=brand, model=model, limit=None,
		                                   offset=0)
		return len(items)

	def list_gens(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None,
			sort: Optional[str] = None
	) -> List[CarGenEntity]:
		items = self._cars
		if brand_model_id:
			items = [c for c in items if (c.brand_model_id or c.id) == brand_model_id]
		if brand:
			items = [c for c in items if c.brand.lower() == brand.lower()]
		if model:
			items = [c for c in items if c.model.lower() == model.lower()]
		return list(items)

	def get_by_id(self, car_id: str):
		return next((c for c in self._cars if c.id == car_id), None)

	def get_by_brand_model_id(self, brand_model_id: str, *, body_type: Optional[str] = None):
		items = [c for c in self._cars if (c.brand_model_id or c.id) == brand_model_id]
		if body_type:
			filtered = [c for c in items if c.body_type == body_type]
			if filtered:
				items = filtered
		return items[0] if items else None

	def search_models(self, q: str, *, limit: int = 20) -> List[CarModelEntity]:
		qq = q.lower()
		items = self.unique_models_by_year()
		return [
			c for c in items
			if qq in f"{c.brand} {c.model}".lower()
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

	def get_filters_meta(self) -> FiltersEntity:
		body_types = sorted({c.body_type for c in self._cars if c.body_type})
		brands = sorted({c.brand for c in self._cars if c.brand})
		models = sorted({c.model for c in self._cars if c.model})
		return FiltersEntity(
			bodyTypes=body_types,
			fuels=[],
			transmissions=[],
			brands=brands,
			models=models,
		)

	def unique_models_by_year(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None,
			limit: Optional[int] = None,
			offset: int = 0
	) -> List[CarModelEntity]:
		items = self._cars
		if brand_model_id:
			items = [c for c in items if (c.brand_model_id or c.id) == brand_model_id]
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
					brand_model_id=c.brand_model_id,
				)
		results = sorted(unique.values(),
		                 key=lambda x: (x.start_year if x.start_year is not None else 10 ** 9, x.brand, x.model))
		if offset:
			results = results[offset:]
		return results[:limit] if limit is not None else results
