from typing import List, Optional

from sqlalchemy import select, or_, text, func
from sqlalchemy.orm import Session

from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity
from app.models.CarModelGenInfo import CarModelGenInfo
from app.models.CarModelInfo import CarModelInfo


def _row_to_model_entity(row) -> CarModelEntity:
    return CarModelEntity(
        id=row.get("id"),
        brand=row.get("make"),
        model=row.get("model"),
        start_year=row.get("start_year"),
        end_year=row.get("end_year"),
    )


def _row_to_gen_entity(row) -> CarGenEntity:
    return CarGenEntity(
        id=str(row.get("id")),
        brand=row.get("make"),
        model=row.get("model"),
        year_from=row.get("year_from"),
        year_to=row.get("year_to"),
        body_type=row.get("body_type", ""),
        fuel=row.get("engine_type", ""),
        transmission=row.get("transmission_type", ""),
    )


class SQLAlchemyCarsRepository:
    def __init__(self, session: Session):
        self._session = session

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
        stmt = select(CarModelGenInfo)

        if brand:
            stmt = stmt.where(CarModelGenInfo.make.ilike(brand))
        if model:
            stmt = stmt.where(CarModelGenInfo.model.ilike(model))
        rows = self._session.execute(stmt).scalars().all()
        return [r.to_entity for r in rows]

    def get_by_id(self, car_id: str) -> Optional[CarGenEntity]:
        row = self._session.get(CarModelGenInfo, car_id)
        return row.to_entity if row else None

    def search_models(self, q: str, *, limit: int = 20) -> List[CarModelEntity]:
        # TODO переделать под sql функцию
        pattern = f"%{q}%"

        stmt = (
            select(CarModelInfo)
            .where(
                or_(
                    CarModelInfo.make.ilike(pattern),
                    CarModelInfo.model.ilike(pattern),
                )
            )
            .limit(limit)
        )

        rows = self._session.execute(stmt).scalars().all()
        return [r.to_entity for r in rows]

    def popular(self, *, limit: int = 10) -> List[CarModelEntity]:
        # пока заглушка — можно заменить на рейтинг/просмотры
        stmt = select(CarModelInfo).limit(limit)
        rows = self._session.execute(stmt).scalars().all()
        return [r.to_entity for r in rows]

    def similar(self, car_id: str, *, limit: int = 10) -> List[CarGenEntity]:
        base = self._session.get(CarModelGenInfo, car_id)
        if not base:
            return []

        stmt = (
            select(CarModelGenInfo)
            .where(
                CarModelGenInfo.id != car_id,
                or_(
                    CarModelGenInfo.make == base.make,
                    CarModelGenInfo.body_type == base.body_type,
                )
            )
            .limit(limit)
        )

        rows = self._session.execute(stmt).scalars().all()
        return [r.to_entity for r in rows]

    def unique_models_by_year(
            self, *, brand: Optional[str] = None, model: Optional[str] = None
    ) -> List[CarModelEntity]:
        if self._session.bind.dialect.name == "sqlite":
            stmt = select(
                func.min(CarModelGenInfo.id).label("id"),
                CarModelGenInfo.make.label("make"),
                CarModelGenInfo.model.label("model"),
                func.min(CarModelGenInfo.year_from).label("start_year"),
                func.max(CarModelGenInfo.year_to).label("end_year"),
            ).group_by(CarModelGenInfo.make, CarModelGenInfo.model).order_by(
                CarModelGenInfo.make, CarModelGenInfo.model
            )

            if brand is not None:
                stmt = stmt.where(CarModelGenInfo.make.ilike(brand))
            if model is not None:
                stmt = stmt.where(CarModelGenInfo.model.ilike(model))

            rows = self._session.execute(stmt).mappings().all()
            return [_row_to_model_entity(row) for row in rows]

        params = {}
        args = []

        if brand is not None:
            params["brand"] = brand
            args.append(":brand")
        if model is not None:
            params["model"] = model
            args.append(":model")

        query = text(f"select * from get_unique_models_with_year_range({', '.join(args)})")
        rows = self._session.execute(query, params).mappings().all()
        return [_row_to_model_entity(row) for row in rows]
