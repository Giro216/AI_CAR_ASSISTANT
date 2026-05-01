from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.entity.CarEntity import CarEntity
from app.models.CarModel import CarModel


class SQLAlchemyCarsRepository:
    def __init__(self, session: Session):
        self._session = session

    def list(
            self,
            *,
            brand: Optional[str] = None,
            model: Optional[str] = None,
            sort: Optional[str] = None
    ) -> List[CarEntity]:
        stmt = select(CarModel)

        if brand:
            stmt = stmt.where(CarModel.make.ilike(brand))
        if model:
            stmt = stmt.where(CarModel.model.ilike(model))

        # пример сортировки
        if sort == "year_desc":
            stmt = stmt.order_by(CarModel.year_from.desc(), CarModel.year_to.desc())
        elif sort == "year_asc":
            stmt = stmt.order_by(CarModel.year_from.asc(), CarModel.year_to.asc())

        rows = self._session.execute(stmt).scalars().all()
        return [r.to_entity for r in rows]

    def get_by_id(self, car_id: str) -> Optional[CarEntity]:
        row = self._session.get(CarModel, car_id)
        return row.to_entity if row else None

    def search(self, q: str, *, limit: int = 20) -> List[CarEntity]:
        pattern = f"%{q}%"

        stmt = (
            select(CarModel)
            .where(
                or_(
                    CarModel.make.ilike(pattern),
                    CarModel.model.ilike(pattern),
                )
            )
            .limit(limit)
        )

        rows = self._session.execute(stmt).scalars().all()
        return [r.to_entity for r in rows]

    def popular(self, *, limit: int = 10) -> List[CarEntity]:
        # пока заглушка — можно заменить на рейтинг/просмотры
        stmt = select(CarModel).limit(limit)
        rows = self._session.execute(stmt).scalars().all()
        return [r.to_entity for r in rows]

    def similar(self, car_id: str, *, limit: int = 10) -> List[CarEntity]:
        base = self._session.get(CarModel, car_id)
        if not base:
            return []

        stmt = (
            select(CarModel)
            .where(
                CarModel.id != car_id,
                or_(
                    CarModel.make == base.make,
                    CarModel.body_type == base.body_type,
                )
            )
            .limit(limit)
        )

        rows = self._session.execute(stmt).scalars().all()
        return [r.to_entity for r in rows]
