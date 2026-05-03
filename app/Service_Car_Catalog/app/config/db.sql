create materialized view cars_main_info_view as
with car_name as (select model.id, m.name as make, model.name as model
                  from model
                           join make m on model.make_id = m.id)
select c.id::text as id,
       car_name.make,
       car_name.model,
       g.year_from,
       g.year_to,
       b.type     as body_type,
       e.engine_type,
       t.type     as transmission_type
from car c
         join generation g on c.generation_id = g.id
         join car_name on g.model_id = car_name.id
         join body b on c.body_id = b.id
         join engine e on c.engine_id = e.id
         join transmission t on c.transmission_id = t.id;

create materialized view unique_models_with_year_range as
select id,
       make,
       model,
       start_year,
       end_year
from (select distinct on (make, model) id,
                                       make,
                                       model,
                                       min(year_from) over (partition by make, model) as start_year,
                                       max(year_to) over (partition by make, model)   as end_year
      from cars_main_info_view
      order by make, model, year_from) as t
order by make, model;

create or replace function get_unique_models_with_year_range(p_make text default '%%', p_model text default '%%')
    returns setof unique_models_with_year_range
    language sql
as
$$
select *
from unique_models_with_year_range
where make ilike p_make
  and model ilike p_model
order by make, model;
$$;
