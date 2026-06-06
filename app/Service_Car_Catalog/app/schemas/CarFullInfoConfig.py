from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.schemas.image import ImageResponse


class CarFullInfoConfig(BaseModel):
	# Enable ORM attribute loading for CarFullInfoMV rows.
	model_config = ConfigDict(from_attributes=True)
	# Общая информация
	brand_model_id: int
	make: Optional[str] = None
	model: Optional[str] = None
	generation: Optional[str] = None
	series: Optional[str] = None
	trim: Optional[str] = None
	year_from: Optional[int] = None
	year_to: Optional[int] = None
	body_type: Optional[str] = None
	doors_count: Optional[int] = None
	battery_id: Optional[int] = None

	# Размеры
	length_mm: Optional[int] = None
	width_mm: Optional[int] = None
	height_mm: Optional[int] = None
	wheelbase_mm: Optional[int] = None
	front_track_mm: Optional[int] = None
	rear_track_mm: Optional[int] = None
	ground_clearance_mm: Optional[int] = None

	# Объём и масса
	curb_weight_kg: Optional[int] = None
	payload_kg: Optional[int] = None
	full_weight_kg: Optional[int] = None
	min_trunk_capacity_l: Optional[int] = None
	max_trunk_capacity_l: Optional[int] = None

	# Двигатель
	engine_id_unique: Optional[int] = None
	engine_type: Optional[str] = None
	cylinder_layout: Optional[str] = None
	number_of_cylinders: Optional[int] = None
	valves_per_cylinder: Optional[int] = None
	boost_type: Optional[str] = None
	capacity_cm3: Optional[int] = None
	max_power_kw: Optional[int] = None
	engine_hp: Optional[int] = None
	maximum_torque_n_m: Optional[int] = None

	# Трансмиссия
	transmission_id_unique: Optional[int] = None
	transmission_type: Optional[str] = None
	number_of_gears: Optional[int] = None
	drive_wheels: Optional[str] = None

	# Эксплуатационные показатели
	acceleration_0_100_km_h_s: Optional[float] = None
	max_speed_km_per_h: Optional[int] = None
	fuel_grade: Optional[str] = None
	fuel_tank_capacity_l: Optional[float] = None
	mixed_fuel_consumption_per_100_km_l: Optional[float] = None
	city_fuel_per_100km_l: Optional[float] = None
	highway_fuel_per_100km_l: Optional[float] = None
	emission_standards: Optional[str] = None

	# Подвеска и тормоза
	front_suspension: Optional[str] = None
	back_suspension: Optional[str] = None
	front_brakes: Optional[str] = None
	rear_brakes: Optional[str] = None

	imageUrl: List[Optional[str]] = None
	imageMeta: Optional[ImageResponse] = None
