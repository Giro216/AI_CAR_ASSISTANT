from typing import Protocol, List, Optional, runtime_checkable

from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity


@runtime_checkable
class CarsRepository(Protocol):
    def list_models(
            self,
            *,
            brand: Optional[str] = None,
            model: Optional[str] = None,
            sort: Optional[str] = None
    ) -> List[CarModelEntity]: ...

    def list_gens(
            self,
            *,
            brand: Optional[str] = None,
            model: Optional[str] = None,
            sort: Optional[str] = None
    ) -> List[CarGenEntity]: ...

    def get_by_id(self, car_id: str) -> Optional[CarGenEntity]: ...

    def search_models(self, q: str, *, limit: int = 20) -> List[CarModelEntity]: ...

    def popular(self, *, limit: int = 10) -> List[CarModelEntity]: ...

    def similar(self, car_id: str, *, limit: int = 10) -> List[CarModelEntity]: ...

    def unique_models_by_year(self, *, brand: Optional[str] = None) -> List[CarModelEntity]: ...
