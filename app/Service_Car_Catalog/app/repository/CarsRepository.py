from typing import Protocol, List, Optional, runtime_checkable

from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity
from app.entity.FiltersEntity import FiltersEntity


@runtime_checkable
class CarsRepository(Protocol):
	def list_models(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None,
			sort: Optional[str] = None,
			limit: int = 50,
			offset: int = 0
	) -> List[CarModelEntity]: ...

	def count_models(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None
	) -> int: ...

	def list_gens(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str],
			model: Optional[str],
	) -> List[CarGenEntity]: ...

	def get_by_id(self, car_id: str) -> Optional[CarGenEntity]: ...

	def get_by_brand_model_id(self, brand_model_id: str, *, body_type: Optional[str] = None) -> Optional[
		CarGenEntity]: ...

	def search_models(self, q: str, *, limit: int = 20) -> List[CarModelEntity]: ...

	def popular(self, *, limit: int = 10) -> List[CarModelEntity]: ...

	def similar(self, car_id: str, *, limit: int = 10) -> List[CarModelEntity]: ...

	def get_filters_meta(self) -> FiltersEntity: ...

	def unique_models_by_year(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None,
			limit: Optional[int] = None,
			offset: int = 0
	) -> List[CarModelEntity]: ...
