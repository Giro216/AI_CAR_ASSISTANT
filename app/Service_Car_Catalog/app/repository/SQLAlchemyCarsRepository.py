from typing import List, Optional

from sqlalchemy import select, or_, text, func, and_
from sqlalchemy.orm import Session

from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity
from app.entity.FiltersEntity import FiltersEntity
from app.models.CarFullInfoMV import CarFullInfoMV
from app.models.CarModelGenInfo import CarModelGenInfo
from app.models.CarModelInfo import CarModelInfo
from app.models.FiltersModel import FiltersModel


def _row_to_model_entity(row) -> CarModelEntity:
	return CarModelEntity(
		id=row.get("id"),
		brand_model_id=row.get("brand_model_id"),
		brand=row.get("make"),
		model=row.get("model"),
		start_year=row.get("start_year"),
		end_year=row.get("end_year"),
	)


def _row_to_gen_entity(row) -> CarGenEntity:
	return CarGenEntity(
		id=str(row.get("id")),
		brand_model_id=row.get("brand_model_id"),
		brand=row.get("make"),
		model=row.get("model"),
		generation=row.get("generation"),
		gen_comment=row.get("series"),
		year_from=row.get("year_from"),
		year_to=row.get("year_to", None),
		body_type=row.get("body_type", None),
	)


class SQLAlchemyCarsRepository:
	def __init__(self, session: Session):
		self._session = session

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
		return self.unique_models_by_filters(
			brand_model_id=brand_model_id,
			brand=brand,
			model=model,
			limit=limit,
			offset=offset,
		)

	def count_models(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None
	) -> int:
		if self._session.bind.dialect.name == "sqlite":
			stmt = select(CarModelGenInfo.make, CarModelGenInfo.model)
			if brand_model_id is not None:
				stmt = stmt.where(func.coalesce(CarModelGenInfo.brand_model_id, CarModelGenInfo.id) == brand_model_id)
			if brand is not None:
				stmt = stmt.where(CarModelGenInfo.make.ilike(brand))
			if model is not None:
				stmt = stmt.where(CarModelGenInfo.model.ilike(model))
			stmt = stmt.group_by(CarModelGenInfo.make, CarModelGenInfo.model)
			count_stmt = select(func.count()).select_from(stmt.subquery())
			return int(self._session.execute(count_stmt).scalar_one())

		params = {
			"brand_model_id": brand_model_id if brand_model_id is not None else "%%",
			"brand": brand if brand is not None else "%%",
			"model": model if model is not None else "%%",
			"limit": None,
			"offset": 0,
		}
		query = text(
			"select count(*) as total from get_unique_models_with_year_range(:brand_model_id, :brand, :model, :limit, :offset)"
		)
		row = self._session.execute(query, params).mappings().first()
		return int(row["total"]) if row and row.get("total") is not None else 0

	def list_gens(
			self,
			*,
			brand_model_id: Optional[str] = None,
			brand: Optional[str] = None,
			model: Optional[str] = None,
	) -> List[CarGenEntity]:
		if self._session.bind.dialect.name == "sqlite":
			stmt = select(CarModelGenInfo)
			if brand_model_id is not None:
				stmt = stmt.where(func.coalesce(CarModelGenInfo.brand_model_id, CarModelGenInfo.id) == brand_model_id)
			if brand is not None:
				stmt = stmt.where(CarModelGenInfo.make.ilike(brand))
			if model is not None:
				stmt = stmt.where(CarModelGenInfo.model.ilike(model))
			rows = self._session.execute(stmt).scalars().all()
			return [r.to_entity for r in rows]

		return self.get_car_models_gens_list(brand_model_id=brand_model_id, brand=brand, model=model)

	def get_by_id(self, car_id: str) -> Optional[CarGenEntity]:
		row = self._session.get(CarModelGenInfo, car_id)
		return row.to_entity if row else None

	def get_by_brand_model_id(self, brand_model_id: int, *, body_type: Optional[str] = None) -> Optional[CarGenEntity]:
		stmt = select(CarModelGenInfo).where(
			func.coalesce(CarModelGenInfo.brand_model_id, CarModelGenInfo.id) == brand_model_id)
		if body_type:
			stmt = stmt.where(CarModelGenInfo.body_type == body_type)
		row = self._session.execute(stmt).scalars().first()
		if row:
			return row.to_entity
		# fallback для совместимости со старыми данными, где brand_model_id ещё не заполнен
		if body_type:
			stmt = select(CarModelGenInfo).where(CarModelGenInfo.id == brand_model_id,
			                                     CarModelGenInfo.body_type == body_type)
			row = self._session.execute(stmt).scalars().first()
			return row.to_entity if row else None
		row = self._session.get(CarModelGenInfo, brand_model_id)
		return row.to_entity if row else None

	def get_full_info(self, *, brand_model_id: str, generation: str, body_type: Optional[str] = None):
		lookup_id = brand_model_id
		if isinstance(brand_model_id, str) and brand_model_id.isdigit():
			lookup_id = int(brand_model_id)
		stmt = select(CarFullInfoMV).where(
			and_(CarFullInfoMV.brand_model_id == lookup_id, CarFullInfoMV.generation == generation)
		)
		if body_type:
			stmt = stmt.where(CarFullInfoMV.body_type == body_type)
		return list(self._session.execute(stmt).scalars().all())

	def search_models(self, q: str, *, limit: int = 20) -> List[CarModelEntity]:
		# TODO переделать под sql функцию
		pattern = f"%{q}%"

		stmt = (
			select(CarModelInfo)
			.where(
				or_(
					CarModelInfo.make.ilike(pattern),
					CarModelInfo.model.ilike(pattern),
					func.concat(CarModelInfo.make, " ", CarModelInfo.model).ilike(pattern),
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

	def unique_models_by_filters(
			self, *, brand_model_id: Optional[str] = None, brand: Optional[str] = None, model: Optional[str] = None,
			limit: Optional[int] = None, offset: int = 0
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

			if brand_model_id is not None:
				stmt = stmt.where(func.coalesce(CarModelGenInfo.brand_model_id, CarModelGenInfo.id) == brand_model_id)
			if brand is not None:
				stmt = stmt.where(CarModelGenInfo.make.ilike(brand))
			if model is not None:
				stmt = stmt.where(CarModelGenInfo.model.ilike(model))
			if limit is not None:
				stmt = stmt.limit(limit)
			if offset:
				stmt = stmt.offset(offset)

			rows = self._session.execute(stmt).mappings().all()
			return [_row_to_model_entity(row) for row in rows]

		params = {
			"brand_model_id": brand_model_id if brand_model_id is not None else "%%",
			"brand": brand if brand is not None else "%%",
			"model": model if model is not None else "%%",
			"limit": limit,
			"offset": offset,
		}

		query = text(
			"select * from get_unique_models_with_year_range(:brand_model_id, :brand, :model, :limit, :offset)")
		rows = self._session.execute(query, params).mappings().all()
		return [_row_to_model_entity(row) for row in rows]

	def get_car_models_gens_list(self, brand_model_id=None, brand=None, model=None) -> List[CarGenEntity]:
		if brand_model_id is None and (brand is None or not str(brand).strip()):
			raise ValueError("brand_model_id or brand is required")
		if brand_model_id is None and (model is None or not str(model).strip()):
			raise ValueError("brand_model_id or model is required")

		params = {
			"brand_model_id": str(brand_model_id) if brand_model_id is not None else "%%",
			"brand": brand if brand is not None and str(brand).strip() else "%%",
			"model": model if model is not None and str(model).strip() else "%%",
		}
		query = text("select * from get_car_models_gens_list(:brand_model_id, :brand, :model)")
		rows = self._session.execute(query, params).mappings().all()
		return [_row_to_gen_entity(row) for row in rows]

	def get_filters_meta(self) -> FiltersEntity:
		stmt = select(FiltersModel)
		items = self._session.execute(stmt).scalars().all()
		body_types = sorted({c.body_type for c in items if c.body_type})
		fuels = sorted({c.engine_type for c in items if c.engine_type})
		transmissions = sorted({c.transmission_type for c in items if c.transmission_type})
		brands = sorted({c.make for c in items if c.make})
		models = sorted({c.model for c in items if c.model})
		return FiltersEntity(bodyTypes=body_types, fuels=fuels, transmissions=transmissions, brands=brands,
		                     models=models)
