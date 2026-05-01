from typing import Protocol, List, Optional, runtime_checkable

from app.entity.CarEntity import CarEntity


@runtime_checkable
class CarsRepository(Protocol):
    def list(
            self,
            *,
            brand: Optional[str] = None,
            model: Optional[str] = None,
            sort: Optional[str] = None
    ) -> List[CarEntity]: ...

    def get_by_id(self, car_id: str) -> Optional[CarEntity]: ...

    def search(self, q: str, *, limit: int = 20) -> List[CarEntity]: ...

    def popular(self, *, limit: int = 10) -> List[CarEntity]: ...

    def similar(self, car_id: str, *, limit: int = 10) -> List[CarEntity]: ...
