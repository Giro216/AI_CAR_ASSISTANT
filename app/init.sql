create table IF NOT EXISTS make
(
    id   SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS model
(
    id      SERIAL PRIMARY KEY,
    make_id INT REFERENCES make (id),
    name    TEXT
);

CREATE TABLE IF NOT EXISTS generation
(
    id        SERIAL PRIMARY KEY,
    model_id  INT REFERENCES model (id),
    name      TEXT, -- raw
    year_from INT,
    year_to   INT
);

CREATE TABLE IF NOT EXISTS body
(
    id   SERIAL PRIMARY KEY,
    type TEXT -- sedan, hatchback, suv
);

CREATE TABLE IF NOT EXISTS engine
(
    id                  SERIAL PRIMARY KEY,
    engine_type         TEXT, -- gasoline/diesel/hybrid
    cylinder_layout     TEXT,
    number_of_cylinders INT,
    valves_per_cylinder INT,
    boost_type          TEXT,
    capacity_cm3        INT,
    max_power_kw        INT,
    engine_hp           INT,
    maximum_torque_n_m  FLOAT
);

CREATE TABLE IF NOT EXISTS transmission
(
    id              SERIAL PRIMARY KEY,
    type            TEXT, -- manual/automatic/robot
    number_of_gears INT,
    drive_wheels    TEXT  -- fwd/rwd/awd/4wd
);

CREATE TABLE battery
(
    id                SERIAL PRIMARY KEY,
    battery_capacity_kw_per_h FLOAT,
    electric_range_km INT
);

-- alter table battery alter column battery_capacity_kw_per_h type FLOAT;

CREATE TABLE IF NOT EXISTS car
(
    id                   SERIAL PRIMARY KEY,
    generation_id        INT REFERENCES generation (id),

    -- weak structured
    series               TEXT,
    trim                 TEXT,

    body_id              INT REFERENCES body (id),
    engine_id            INT REFERENCES engine (id),
    transmission_id      INT REFERENCES transmission (id),
    battery_id           INT REFERENCES battery (id),

    -- размеры
    length_mm            INT,
    width_mm             INT,
    height_mm            INT,
    wheelbase_mm         INT,
    front_track_mm       INT,
    rear_track_mm        INT,

    -- масса
    curb_weight_kg       INT,
    payload_kg           INT,
    full_weight_kg       INT,
    ground_clearance_mm  INT,

    -- багажник
    min_trunk_capacity_l INT,
    max_trunk_capacity_l INT,

    -- динамика
    "acceleration_0_100_km/h_s" FLOAT,
    max_speed_km_per_h   INT,

    -- топливо
    fuel_grade           TEXT,
    fuel_tank_capacity_l INT,
    mixed_fuel_consumption_per_100_km_l FLOAT,
    city_fuel_per_100km_l FLOAT,
    highway_fuel_per_100km_l FLOAT,
    emission_standards   TEXT,

    -- подвеска/тормоза
    front_suspension     TEXT,
    back_suspension      TEXT,
    front_brakes         TEXT,
    rear_brakes          TEXT
);

-- Indexes for joins (FK lookups)
CREATE INDEX IF NOT EXISTS idx_model_make_id
    ON model (make_id);

CREATE INDEX IF NOT EXISTS idx_generation_model_id
    ON generation (model_id);

CREATE INDEX IF NOT EXISTS idx_car_generation_id
    ON car (generation_id);

CREATE INDEX IF NOT EXISTS idx_car_body_id
    ON car (body_id);

CREATE INDEX IF NOT EXISTS idx_car_engine_id
    ON car (engine_id);

CREATE INDEX IF NOT EXISTS idx_car_transmission_id
    ON car (transmission_id);

CREATE INDEX IF NOT EXISTS idx_car_battery_id
    ON car (battery_id);

-- Indexes for dictionary search / filtering
CREATE INDEX IF NOT EXISTS idx_make_name
    ON make (name);

CREATE INDEX IF NOT EXISTS idx_model_name
    ON model (name);

CREATE INDEX IF NOT EXISTS idx_generation_name
    ON generation (name);

CREATE INDEX IF NOT EXISTS idx_generation_year_from
    ON generation (year_from);

CREATE INDEX IF NOT EXISTS idx_generation_year_to
    ON generation (year_to);

CREATE INDEX IF NOT EXISTS idx_body_type
    ON body (type);

CREATE INDEX IF NOT EXISTS idx_engine_engine_type
    ON engine (engine_type);

CREATE INDEX IF NOT EXISTS idx_transmission_type
    ON transmission (type);

CREATE INDEX IF NOT EXISTS idx_transmission_drive_wheels
    ON transmission (drive_wheels);

-- Composite indexes for frequent combined filters
CREATE INDEX IF NOT EXISTS idx_generation_model_years
    ON generation (model_id, year_from, year_to);

CREATE INDEX IF NOT EXISTS idx_car_generation_body_engine
    ON car (generation_id, body_id, engine_id);
