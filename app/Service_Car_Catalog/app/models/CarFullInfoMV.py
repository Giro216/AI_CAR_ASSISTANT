from sqlalchemy import Column, Integer, String, Float, Text

from app.config.database import Base


class CarFullInfoMV(Base):
	__tablename__ = 'car_full_info_mv'

	# ----- ОБЩАЯ ИНФОРМАЦИЯ -----
	main_info_id = Column(Integer, primary_key=True, index=True)
	brand_model_id = Column(Integer, nullable=False)
	make = Column(String(50))
	model = Column(String(100))
	generation = Column(String(100))
	series = Column(String(100))
	trim = Column(String(100))
	year_from = Column(Integer)
	year_to = Column(Integer)
	body_type = Column(String(50))
	doors_count = Column(Integer)
	engine_id = Column(Integer)
	transmission_id = Column(Integer)
	car_id = Column(Integer)
	generation_id = Column(Integer)
	body_id = Column(Integer)
	battery_id = Column(Integer)

	# ----- РАЗМЕРЫ -----
	length_mm = Column(Integer)
	width_mm = Column(Integer)
	height_mm = Column(Integer)
	wheelbase_mm = Column(Integer)
	front_track_mm = Column(Integer)
	rear_track_mm = Column(Integer)
	ground_clearance_mm = Column(Integer)

	# ----- ОБЪЁМ И МАССА -----
	curb_weight_kg = Column(Integer)
	payload_kg = Column(Integer)
	full_weight_kg = Column(Integer)
	min_trunk_capacity_l = Column(Integer)
	max_trunk_capacity_l = Column(Integer)

	# ----- ДВИГАТЕЛЬ -----
	engine_id_unique = Column(Integer)
	engine_type = Column(String(50))
	cylinder_layout = Column(String(30))
	number_of_cylinders = Column(Integer)
	valves_per_cylinder = Column(Integer)
	boost_type = Column(String(50))
	capacity_cm3 = Column(Integer)
	max_power_kw = Column(Integer)
	engine_hp = Column(Integer)
	maximum_torque_n_m = Column(Integer)

	# ----- ТРАНСМИССИЯ -----
	transmission_id_unique = Column(Integer)
	transmission_type = Column(String(50))
	number_of_gears = Column(Integer)
	drive_wheels = Column(String(20))

	# ----- ЭКСПЛУАТАЦИОННЫЕ ПОКАЗАТЕЛИ -----
	acceleration_0_100_km_h_s = Column("acceleration_0_100_km/h_s", Float)
	max_speed_km_per_h = Column(Integer)
	fuel_grade = Column(String(50))
	fuel_tank_capacity_l = Column(Float)
	mixed_fuel_consumption_per_100_km_l = Column(Float)
	city_fuel_per_100km_l = Column(Float)
	highway_fuel_per_100km_l = Column(Float)
	emission_standards = Column(String(50))

	# ----- ПОДВЕСКА И ТОРМОЗА -----
	front_suspension = Column(Text)
	back_suspension = Column(Text)
	front_brakes = Column(String(100))
	rear_brakes = Column(String(100))

	def __repr__(self):
		return f"<CarFullInfoMV {self.make} {self.model} {self.generation}>"
