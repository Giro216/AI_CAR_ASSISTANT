-- tables


CREATE TABLE IF NOT EXISTS user_favorites (
    user_id UUID NOT NULL,    
    car_id VARCHAR(100) NOT NULL,
    
    PRIMARY KEY (user_id, car_id)
);

CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites (user_id);

CREATE TABLE IF NOT EXISTS car_unique_configs
(
    id             SERIAL PRIMARY KEY,

    brand_model_id INT       NOT NULL,
    generation     TEXT,
    series         TEXT,
    body_type      TEXT,

    created_at     TIMESTAMP NOT NULL DEFAULT now(),

    UNIQUE (
            brand_model_id,
            generation,
            series,
            body_type
        )
);

CREATE TABLE IF NOT EXISTS car_config_photos
(
    id         BIGSERIAL PRIMARY KEY,

    config_id  INT       NOT NULL
        REFERENCES car_unique_configs (id),

    url        TEXT      NOT NULL,
    priority   INTEGER   NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT now(),

    UNIQUE (config_id, url),
    UNIQUE (config_id, priority)
);

CREATE TABLE IF NOT EXISTS brand_model_photos
(
    id             BIGSERIAL PRIMARY KEY,

    brand_model_id INT       NOT NULL,

    url            TEXT      NOT NULL,
    priority       INTEGER   NOT NULL,

    created_at     TIMESTAMP NOT NULL DEFAULT now(),

    UNIQUE (brand_model_id, url),
    UNIQUE (brand_model_id, priority)
);

-- materialized view

create materialized view cars_models as
select model.id,
       m.name     as make,
       model.name as model
from model
         join make m on model.make_id = m.id;

create materialized view cars_main_info_view as
select c.id::text     as id,
       cars_models.id as brand_model_id,
       cars_models.make,
       cars_models.model,
       g.name         as generation,
       c.series,
       c.trim,
       g.year_from,
       g.year_to,
       b.type         as body_type,
       c.doors_count,
       e.id           as engine_id,
       t.id           as transmission_id
from car c
         join generation g on c.generation_id = g.id
         join cars_models on g.model_id = cars_models.id
         join body b on c.body_id = b.id
         join engine e on c.engine_id = e.id
         join transmission t on c.transmission_id = t.id
order by make, model, generation, series;

create materialized view unique_models_with_year_range as
select id,
       brand_model_id,
       make,
       model,
       start_year,
       end_year
from (select distinct on (make, model) id,
                                       brand_model_id,
                                       make,
                                       model,
                                       min(year_from) over (partition by brand_model_id, make, model) as start_year,
                                       max(year_to) over (partition by brand_model_id, make, model)   as end_year
      from cars_main_info_view
      order by make, model, year_from) as t
order by brand_model_id, make, model;

create materialized view all_filters_metadata as
select distinct c.id,
                cm.make,
                cm.model,
                b.type as body_type,
                e.engine_type,
                t.type as transmission_type
from cars_models cm
         join generation g on cm.id = g.model_id
         join car c on g.id = c.generation_id
         join body b on c.body_id = b.id
         join engine e on c.engine_id = e.id
         join transmission t on c.transmission_id = t.id
order by cm.make, cm.model, body_type, engine_type, transmission_type;

-- Создаем материализованное представление с группировкой колонок
CREATE MATERIALIZED VIEW car_full_info_mv AS
SELECT
    -- ===== ОБЩАЯ ИНФОРМАЦИЯ =====
    cmiv.id AS main_info_id,
    cmiv.brand_model_id,
    cmiv.make,
    cmiv.model,
    cmiv.generation,
    cmiv.series,
    cmiv.trim,
    cmiv.year_from,
    cmiv.year_to,
    cmiv.body_type,
    cmiv.doors_count,
    cmiv.engine_id,
    cmiv.transmission_id,
    c.id    AS car_id,
    c.generation_id,
    c.body_id,
    c.battery_id,

    -- ===== РАЗМЕРЫ =====
    c.length_mm,
    c.width_mm,
    c.height_mm,
    c.wheelbase_mm,
    c.front_track_mm,
    c.rear_track_mm,
    c.ground_clearance_mm,

    -- ===== ОБЪЁМ И МАССА =====
    c.curb_weight_kg,
    c.payload_kg,
    c.full_weight_kg,
    c.min_trunk_capacity_l,
    c.max_trunk_capacity_l,

    -- ===== ДВИГАТЕЛЬ =====
    e.id    AS engine_id_unique,
    e.engine_type,
    e.cylinder_layout,
    e.number_of_cylinders,
    e.valves_per_cylinder,
    e.boost_type,
    e.capacity_cm3,
    e.max_power_kw,
    e.engine_hp,
    e.maximum_torque_n_m,

    -- ===== ТРАНСМИССИЯ =====
    t.id    AS transmission_id_unique,
    t.type  AS transmission_type,
    t.number_of_gears,
    t.drive_wheels,

    -- ===== ЭКСПЛУАТАЦИОННЫЕ ПОКАЗАТЕЛИ =====
    c."acceleration_0_100_km/h_s",
    c.max_speed_km_per_h,
    c.fuel_grade,
    c.fuel_tank_capacity_l,
    c.mixed_fuel_consumption_per_100_km_l,
    c.city_fuel_per_100km_l,
    c.highway_fuel_per_100km_l,
    c.emission_standards,

    -- ===== ПОДВЕСКА И ТОРМОЗА =====
    c.front_suspension,
    c.back_suspension,
    c.front_brakes,
    c.rear_brakes

FROM cars_main_info_view AS cmiv
         JOIN car c ON cmiv.id::text = c.id::text
         JOIN engine e ON cmiv.engine_id = e.id
         JOIN transmission t ON cmiv.transmission_id = t.id;

-- ===== ИНДЕКСЫ ДЛЯ БЫСТРОГО ПОИСКА =====
CREATE INDEX IF NOT EXISTS idx_mv_brand_model_id ON car_full_info_mv (brand_model_id);
CREATE INDEX IF NOT EXISTS idx_mv_body_type ON car_full_info_mv (body_type);
CREATE INDEX IF NOT EXISTS idx_mv_series ON car_full_info_mv (series);
CREATE INDEX IF NOT EXISTS idx_mv_transmission_type ON car_full_info_mv (transmission_type);
CREATE INDEX IF NOT EXISTS idx_mv_drive_wheels ON car_full_info_mv (drive_wheels);

-- Дополнительный составной индекс для самых частых фильтров
CREATE INDEX IF NOT EXISTS idx_mv_brand_body_series ON car_full_info_mv (brand_model_id, body_type, series);

-- functions

create or replace function get_unique_models_with_year_range(
    p_brand_model_id text default '%%',
    p_make text default '%%',
    p_model text default '%%',
    p_limit int default 50,
    p_offset int default 0
)
    returns setof unique_models_with_year_range
    language sql
as
$$
select *
from unique_models_with_year_range
where brand_model_id::text ilike p_brand_model_id
  and make ilike p_make
  and model ilike p_model
order by make, model
limit p_limit offset p_offset;
$$;

create or replace function get_car_models_gens_list(
    p_brand_model_id text,
    p_make text,
    p_model text
)
    returns table
            (
                id             text,
                brand_model_id text,
                make           text,
                model          text,
                generation     text,
                series         text,
                year_from      int,
                year_to        int,
                body_type      text
            )
    language sql
as
$$
select id,
       brand_model_id,
       make,
       model,
       generation,
       series,
       year_from,
       year_to,
       body_type
from (select distinct on (brand_model_id, make, model, generation, body_type) *
      from cars_main_info_view
      where (p_brand_model_id = '%%' or brand_model_id::text ilike p_brand_model_id)
        and make ilike '' || p_make || ''
        and model ilike '' || p_model || '')
         as t
order by year_from desc;
$$;

-- init data

INSERT INTO car_unique_configs (brand_model_id, generation, series, body_type)
SELECT DISTINCT ON
    (brand_model_id, generation, series, body_type)
    brand_model_id, generation, series, body_type
FROM cars_main_info_view
ORDER BY brand_model_id;