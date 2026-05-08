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